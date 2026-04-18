---
title: Claude Code常用命令指北【官网版】
date: 2026-04-13 22:00
tags:
   - 大语言模型
categories:
   - 场景实践
description: 深入解析Claude Code的核心概念与常用命令，涵盖Command、Skill、Rule、Subagent等关键功能的详细介绍与使用技巧，助您掌握现代化AI编程工作流。
---

Work agent在25年风头无两，其中以Claude Code最为显眼。Claude Code一直走在coding agent的最前列，提出了skills、subagent等多种已经成为事实标准的概念。

随后一系列的Coding Agent，如Qoder、Gemini Cli、Qwen Cli、CodeX全部follow CC的主要设计，只要能针对一个agent的原理有所理解，对于其他agent也可以达到一通百通的程度了。

同时，因为commands、skills、rules、subagent这些概念基本上在每个work agent都有存在，所以一旦这些资产沉淀下来，其他的agent也可以顺利复用。

所以依据claude code 的官方文档，加上自己的理解，特意梳理了下相关的slash概念，帮助后续更好的vibe coding。

本文是Claude Code系列的第一篇，介绍基础的概念和操作——预计还有两篇，介绍CC的常见的上下文优化手段与我个人对辅助CC编程的一些思考。

# 基本概念
## Command
command是最直接驱使agent的user prompt。通过直接在CLI或者GUI的输入框输入指令，便可触发CC完成响应。

另外如果指令太长，或者指令可以复用，则可以把指令形成文件，放置到 .cluade/commands/ 目录下面，这样在下次使用的时候，在CLI中直接 输入 slash + command 即可，如下所示：

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/94ab8801_b76cb1b4.png)

## Skill
> 相关内容参考：[https://code.claude.com/docs/zh-CN/skills](https://code.claude.com/docs/zh-CN/skills)
>

Skill可以理解是一个大号的command，把一些复杂或者标准工作沉淀成一套SOP。不过，skill与command最大的不同就是，skill不仅可以主动调用，也可以在vibe coding的时候，claude code可以根据上下文信息分析是否要自动调用skill。那么，如何编写一个skill呢？

人工构建skill指令当然是好的，但是AI时代，我们也可以让CC帮我们完成skill的编写，这里可以使用CC官方的[skill指南](https://code.claude.com/docs/en/skills)和[skill 指令](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)来帮我们创建skill。

有了创建skill的skill之后，就可以通过对话的形式，让claude code帮我创建一些其他skill。举个例子，我希望创建一个获取yuque.com的文档，prompt如下：

`帮我创建一个skill，作用是获取yuque.com中的文档，具体是我给你一个yuque的文档链接（这个链接我可以在chrome中正常访问，因为我在chrome中有登录语雀账号，链接也是我自己的语雀文档链接），你帮我把语雀连接中的文档读出来，并下载到本地，以markdown格式保存`

可以发现，claude code可以自动发现我们刚才写的`skill-create`skill，如下：

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/2b4cdca1_dcdc8b25.png)

具体生成的skill我已经上传到github上了，感兴趣可以[点击](https://github.com/wxxlamp/wxxlamp.github.io/blob/deploy/.claude/skills/yuque-fetcher/SKILL.md)获取。

下面，基于用skill-create生成yuque-fetcher skill，来将一篇语雀文档生成到本地，claude code会遍历所有可用的skill，然后默认调用yuque-doc-downloader skill，进行语雀文章的下载

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/b62727ad_4db8f1a8.png)

结果也是非常的哇塞，虽然图片没有顺利展示，但是基本的的内容都有了。

有个问题是，怎么发现自己的skill是否被调用呢？可以通过~/.claude.json来check skill被后台调用的次数：

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/006b47f7_c3232358.png)

## Rule
> 相关内容参考：[https://code.claude.com/docs/zh-CN/memory](https://code.claude.com/docs/zh-CN/memory#)
>

rule的本质也是一种记忆，cc在每次请求模型的时候都会把完整的rule带给LLM，我们可以通过 /memory 命令进行check：

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/c09f471b_3f295084.png)

rule最常见的使用就是限制claude做一些事情，譬如说最常见的代码规范，我们可以把一些规约性的内容编写成rule提供给CC作为参考。项目级别的rule的位置如下：

```shell
your-project/
├── .claude/
│   ├── CLAUDE.md           # 主项目指令
│   └── rules/
│       ├── code-style.md   # 代码样式指南
│       ├── testing.md      # 测试约定
│       └── security.md     # 安全要求
```

值得注意的是，我们可以通过path属性选择rule对哪些文件生效，如下所示：

```shell
---
paths:
  - "src/api/**/*.ts"
---

# API 开发规则

- 所有 API 端点必须包括输入验证
- 使用标准错误响应格式
- 包括 OpenAPI 文档注释
```

## Hooks
> 相关内容参考：[https://code.claude.com/docs/zh-CN/hooks-guide](https://code.claude.com/docs/zh-CN/hooks-guide)
>

Hook机制使得用户可以更加精准掌控claude code的行为，我们可以在会话前后、脚本执行前后执行各种命令。

根据[cc的官方文档](https://code.claude.com/docs/en/hooks-guide)，可以返现常见的hook周期如下：

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/0700f2c0_ab484b5d.png)

比较经典的hook场景有上下文压缩，我们可以针对某个工程，在每次claude会话关闭的时候都让claude压缩一次上下文存储到本地，然后在下次claude启动的时候再自动读取。

可以参考[claude code的官方例子](https://code.claude.com/docs/en/hooks-guide#get-notified-when-claude-needs-input)，在每次需要人工介入的时候，弹出一个提示，防止任务一直holding：  
![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/799f3c38_07e56628.png)

## MCP
> 相关内容参考：[https://code.claude.com/docs/zh-CN/mcp](https://code.claude.com/docs/zh-CN/mcp)
>

claude在接收到指令的时候，不止会列出所有的skills、rules，还有所有的mcp，Claude Code会根据用户的指令，选择最合适的MCP执行。

不过需要注意的是，mcp的地址与其他诸如skills之类的不一样，用户级别和项目级别的mcp的配置均在 ~/.claude.json中，常见的MCP如下：

| 名称 | 用途说明 | 主要功能 |
| --- | --- | --- |
| sequential-thinking | 用于复杂问题的顺序推理。当需要解决多步骤问题、进行逻辑分析或规划复杂任务时，该服务器帮助逐步构建推理链。 | 多步骤逻辑分析、任务规划、逐步推导结论 |
| jetbrains | 与 JetBrains IDE（如 IntelliJ IDEA、PyCharm、WebStorm 等）集成。 | 允许 AI 直接读取代码、执行重构、运行测试、访问项目结构等 IDE 级操作 |
| browsermcp | 实现浏览器自动化操作，AI 可控制浏览器行为。 | 页面导航、点击元素、填写表单、截图；适用于网页测试、数据抓取、应用调试 |
| puppeteer | 基于 Puppeteer 框架的浏览器自动化，功能与 browsermcp 类似。 | 页面控制、元素操作、执行 JavaScript、生成 PDF/截图；更底层、可编程性强 |
| context7 | 提供对最新编程文档和代码示例的实时访问，超越 AI 训练数据的时效性限制。 | 查询 API 用法、获取最新库文档、检索代码示例、支持版本更新内容检索 |


> 注：browsermcp 与 puppeteer 功能重叠，但 browsermcp 为通用浏览器 MCP 接口，puppeteer 通常特指基于 Chromium 的 Node.js 自动化框架实现。
>

当然mcp也可以配置在项目级别，只需要使用如下命令即可：

```bash
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

## Subagents
> 相关内容参考：[https://code.claude.com/docs/zh-CN/sub-agents#other](https://code.claude.com/docs/zh-CN/sub-agents#other)
>

不同的agent可以使用不同的skill和MCP、有不同的权限、模型和上下文。个人认为，subagent最重要的一点就是上下文的隔离，可以把不同任务用上下文隔离开。这样就会节省很多token，使得模型的回答更加精确。

同时，subagent既然叫做agent，就说明他和主agent的能力几乎一样，subagent也有一块独立的memory空间供其维护长期的上下文，我们可以在创建subagent的时候，显示开启memory存储。

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/d98bd464_7ce7a25c.png)

如何唤醒subagent呢？有两种方式，一种是在cli命令中使用自然语言，如`使用code reviewer 帮我完成cr`或者使用`@`强制要求Claude code使用某agent，如 `使用@‘code reviewer(agent)’帮我完成cr`

当我们创建完subagent之后，它的存储地址和skills、commands一致。如果是项目级别的话，则会存储到`project/.claude/agents/`目录中

举个例子，我们可以创建一个 `code-reviewer`的subagent，帮我们独立于主上下文来review代码。

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/93981e05_7290ccbd.png)

可以看出，系统可以根据自然语言选择出对应的subagent来操作。不过需要注意的是，既然系统可以自动抓取要使用的subagents，那就说明subagents也在memory中占有一席之地。换句话说，subagent也不是越多越好，太多了容易和mcp一样，把上下文的token撑爆。

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/5e29caec_bd6aeec9.png)

## Plugins
> 相关内容参考：[https://code.claude.com/docs/zh-CN/plugins](https://code.claude.com/docs/zh-CN/plugins)
>

Plugin顾名思义，就是插件。它是commands、skill、subagent等的集合。Plugin面向的是一件事务的解决方案。

本篇文章暂不赘述，后续我将创建一个从 语雀网站拉取博客，到自动发布微信公众号、个人网站、小红书的plugin，到时候再演示plugin的打包能力。