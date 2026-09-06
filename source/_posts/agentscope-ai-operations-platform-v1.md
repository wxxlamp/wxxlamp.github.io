---
title: 基于 AgentScope 的 AI 运营平台设计与实践
date: 2026-07-19 23:58
tags:
  - 智能体工程
  - 大模型应用
  - 系统设计
categories:
  - 架构思考
description: 基于AgentScope总结AI运营平台的工程实践，覆盖提示词、状态机、主子Agent、工具治理、联调验证与体验优化。
---

![AI 运营平台](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/52d30cd1_agentscope-ops-platform-cover.png)

> 很多人上手 Agent 开发，第一反应是把 Agent loop 跑起来——模型调工具、拿结果、再进入下一轮。但真正把一个面向运营的 AI 平台做到可用，你会发现 Loop 只是起点。这篇文章基于 AgentScope，聊聊我们在构建 AI 运营平台的过程中，除了 Loop 之外还踩过、想过的那些事：提示词与技能怎么分工、长流程怎么引导、多下游接口怎么保证参数正确。（文中隐去了内部平台地址、系统名称与具体业务数据，只保留可复用的工程实践。）

## 一、核心问题与解决方案

做这类运营智能体，绕不开下面三个核心问题，我把我们最终采用的做法也一并列在后面。

### 核心问题

1. 如何让算法的策略被模型有效识别？

    - 拆分人群圈选、触达、权益等不同领域 agent，各域 agent 维护单独的上下文和 skill
    - 借助 AgentScope，实现 Agent loop 和基本的 skills、mcp 管理

2. 如何正确引导运营操作长流程、不乱操作？

    - workflow + 前端流程渲染
    - ask user question 卡片

3. 如何对接多个下游系统、保证参数的正确？

    - 对接营销投放平台、触达平台、数据仓库、低代码平台、协同文档等多个工具和 MCP
    - 发券、触达等 tools，通过上下文 extract & parse 对应的核心参数，避免模型自己填写

### 架构与解决方案

下图是脱敏后的整体架构示意，你可以对照后文的每个模块来看：

![AI 运营平台架构](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/fc72e4a1_agentscope-ops-platform-architecture.png)

## 二、提示词、技能与会话

### Prompt 与 Skills 分工的思考

如果你刚上手，多半会像我们一样先把主 Agent 的 prompt 写得很简单，把路由和 workflow 管理放到 skill 里。但很快你会发现：模型有时候根本不加载对应的 skill，而是直接依赖 system prompt 自由发挥，整体效果因此打折。这里有两条建议：

1. skills 是渐进式披露和加载。如果一个数据很重要、且每轮对话都会用到，就直接放进 system prompt，不要为了省 token 塞到 skills 里，否则效果会大打折扣；
2. 虽然 system prompt 常被建议控制在 ~500 行以内，但起步阶段不必拘泥于这个限制。你可以先写一个大而全的 system prompt，等效果稳定后，再通过 reference 优化它的长度。

### 动态 prompt 防止 Lost in the Middle

基于 Transformer 的 LLM，注意力容易往两端分散，中间的信息有可能被"遗忘"；再加上压缩机制，agent 还可能把工具的结果压缩掉。所以请记住一条原则：真正重要的信息，不要交给模型自己管理，而要人工干预。

我们的做法是通过 AgentScope 的 middleware 能力，在每轮会话开始时，把重要信息从内存中抽象出来，用 `<Context-Reminder></Context-Reminder>` 标签强制追加到 system prompt 中，以此保证模型对关键信息保持"绝对注意力"。

Context-Reminder 中通常包含这些内容：

`活动基本信息（活动名称、用户ID等）、活动阶段&流程控制、人群信息、外部接口的id等`

### 如何优化 Prompt

我们优化 prompt 的节奏大致分三步：

- step1：根据 agent 的角色、功能，编写最初版 prompt
- step2：不断地增加 prompt 的内容，先把效果堆上来
- step3：效果达到预期后，再把 prompt 的部分内容存到 reference 中渐进式加载

两个注意点：

1. prompt 无需关注工具的入参
2. 不要因为上下文长度，就无脑压缩 prompt

延伸阅读：

1. [Claude 提示词最佳实践](https://platform.claude.com/docs/zh-CN/build-with-claude/prompt-engineering/claude-prompting-best-practices)
2. [prompt-eng-interactive-tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)

### 上下文压缩

上下文过长，一方面会拖慢模型的推理性能，另一方面也会影响推理效果。目前 AgentScope 默认的压缩策略有：压缩思考、压缩工具、模型回话。你可以这样理解它的演进：

1. 借助 AgentScope，默认会把模型的 thinking 过程和工具调用结果都压缩掉，每轮会话只保留用户和模型的 QA；
2. 更进一步的压缩策略，会保留一部分工具结果，同时删除一些无效的对话。

## 三、状态机与 Plan 工具

一次运营活动往往复杂且流程冗长，既要灵活回答用户的问题，也要能引导用户按流程往下走。为此，我们在 system prompt 里动态注入了一套状态机，以最高优先级引导用户。这里有个关键细节：不要把状态机的规则写进 prompt，而是用 hard code 计算模型当前处于哪一步、下一步该做什么。 整体结构（示意）如下：

```json
{
  "currentStage": "阶段标识",
  "currentStep": "当前步骤标识",
  "nextStep": "下一步骤标识",
  "actionType": "independentThinking | callSkill | callAgent"
}
```

在明确当前步骤的同时，也要明确告诉模型：完成这一步应该独立思考、还是调用 skill、还是调用 agent。

为了让步骤能动态流转，我们定制了一套 plan 工具：模型每完成一个步骤就调用它更新进度，系统据此感知内存数据变化，并在下一次 loop 时通过 middleware 把最新步骤喂回给模型。

因为这些步骤都落到了数据库里，运营在前端就能直接看到流程进度，体感会好很多。

## 四、主子 agent

### 什么时候用子 Agent？

先破除一个误区：agent 本质上只是对模型 API 的一层上下文封装，模型其实识别不了"子 agent"（对模型而言它只是一个 tool）。不过相比 skill，子 agent 有独立上下文、可并发执行等好处。所以要不要拆出独立子 agent，你可以用这三条标准来判断：

1. 子任务是否独立？
2. 子任务是否可以并行？
3. 子任务的迭代次数是否过多？

【分工合作】还有一个容易被忽略的组织收益：当有多位算法同学参与时，按领域拆分子 agent，能让每个人对自己 agent 的效果负责——领域边界清晰后，联调更顺，整体项目效果也更有保障。

### 主子 agent 的通信与协作

这里有三条比较实用的经验：

1. 在主 Agent 的 system prompt 里动态注入"当前要调用的子 Agent"，避免子 Agent 任务还没完成、主 Agent 就抢着接管，这能显著提升主 agent 的识别准确性；
2. 强制子 agent 用 json 返回内容，并加一个 `isCompleted=true` 字段来表明自己已完成（部分模型可以通过参数开启结构化 json 输出）；
3. 子 agent 完成后，通过 middleware 机制把返回结果落库；因为 json 格式确定，这些数据可以直接作为后续工具的入参。

### 推理时间过长的优化措施

项目初期测试时，你很可能会遇到 agent 的 reasoning 时间过长的问题。但请注意：别直接关掉 thinking，那会严重损伤效果。基于大模型，我们做了几项优化来降低 reasoning 时间：

1. 上下文压缩：去掉子 agent 的 skill-pre-load 机制，同时调低主 agent 的 thinking token limit；
2. 思考 budget：部分大模型提供 thinking-budget 参数，可以控制模型的思考时长；
3. 调整 top-p 和 temperature。

还有几个方向我们还在持续探索：

1. agent 并行调用；
2. agent 异步调用，主 agent 提前把结果返回给业务；
3. 把 agent 的职责拆得更细，按职责为不同 agent 匹配不同参数的模型。

## 五、工具与 MCP

### 如何保证接口参数的正确性

对接营销投放平台、触达平台这类接口时，最让人担心的就是：模型理解不了参数字段的含义，进而传错参数，譬如渠道 ID、有效期、开始时间。

事实也印证了这一点——初期联调时模型传错字段时有发生，典型的就是人群 SQL。原因在于：哪怕字段定义得再清楚，只要模型上下文里存在很多圈人的 SQL，它就可能随机选错（比如把正式表传成离线表、把权益的 SQL 用成触达的 SQL）。

对此我们采取了三个措施：

1. 在投放平台侧新增一个"参数定义"接口，严格限制入参枚举，并尽可能把定义写丰富；
2. 在运营平台侧，把投放平台的 MCP 封装成 tools，再通过 middleware 以 hardcode 的方式 extract 关键参数（人群 SQL、开始时间、有效期、活动类型等）——这些参数由代码直接传入，不需要模型推理；
3. 加监控：对"模型推理的参数"和"最终调用投放平台的参数"做两次落库，方便后续审计和追踪。

### 工具并发调用踩坑

并发调用工具能减少模型的 loop 次数、提升效果；但要小心：并发修改数据库字段时可能产生数据覆盖，破坏一致性。 这一点在设计并发方案时务必提前评估。

## 六、联调与验证

改完 prompt 和 skill 后，验证对应 feature 往往非常耗时，而且你还很难确定改动是否波及了其他地方。

我们的解法是定制一个脚本，基于编码 Agent 调用平台的 chat 接口，用模型与平台对话，并按约定的约束智能判断平台返回是否符合预期。整套验证会用到这几类 artifact：

1. 一个 e2e 脚本，通过编码 Agent 与平台对话；
2. 平台对话的输出；
3. 平台的运行时日志；
4. 平台模型的 context（只取最后两个数组）。

把上述 artifact 喂给编码 Agent，让它按指示结合本次优化的 feature，分析平台表现是否达标。

需要坦诚说明的是：这个思路目前还处在初期阶段，我们已经跑通了自动对话，但由于不同 agent 的能力都比较 professional，对话结束后仍然依赖算法同学结合日志来做最终分析。

## 七、用户体验的一些措施

### KeepAlive 保活机制

用户长时间不输入时，SSE 流很容易断掉。我们在服务端加了 keepalive 保活机制来避免会话中断——如果你的产品也用 SSE 做流式输出，这个几乎是必备项。

### 断点重试机制

网络抖动（譬如后台服务部署）会导致 chat 断开。为此我们在前端加了断点重试机制，会自动重试三次 chat 会话，尽量让用户无感。

### Ask User Question 卡片

借助 AgentScope，我们把 ask user question 卡片做了优化：模型调用该工具后，用户可以直接选择、填空、完善日期等，交互体验更顺滑。

## 八、未来发展 & 规划

最后，分享几个我们正在推进的方向，也欢迎你一起交流：

1. 多产品、多活动的 auto copilot；
2. 基于用户会话，沉淀不同类型活动的自动纠正机制：用定时任务扫描用户对话，捕捉用户质疑的内容，进而自动优化 skills 和 prompt；
3. 并发调用不同 agent，提高系统的响应速度。
