# 上完 AI 夜校，我想了几个问题

![关于 Agent 边界的思考](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/1618f01f_card-1.png)

最近参加了淘天技术的 AI 夜校。我这段时间正好在做 Agent 相关业务，第一场 Overview 听下来，很多内容都能和手头的开发对上。

回去以后记了几个问题，有些地方我也没完全想清楚。

![模型与程序互补](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/9ae8e51a_card-2.png)

Agent 真能替掉所有软件吗？我个人觉得比较难。LLM 适合处理自然语言和非结构化信息，但输出有概率性。算数、查库、固定流程继续用普通程序，成本低，结果也容易验证。生产系统里，两边基本都要用。

![Model、Agent 与 Harness](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/a4071456_card-3.png)

Model、Agent、Harness 也经常被混在一起。我的理解是：Model 负责生成；Agent 组装上下文、调用工具；记忆、状态恢复、评测和编排还要靠外面的 Harness。开多少个 Subagent，更多是工程实现。

![程序、Skill 与 Subagent 的选型](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/818807ff_card-4.png)

产品同学有时会和我说：“快把这个东西抽成一个 Skill，以后我就不找你了。”

我一般先看确定性。固定流程直接写程序；依赖经验、很难完整程序化的 SOP，可以整理成 Skill；任务能够独立执行或者并行处理，再考虑 Subagent。这个划分肯定不完美，目前用起来还算顺手。

![Agent 的一些应用场景](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/e2f4e6ea_card-5.png)

![开发时要处理的问题](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/c800498c_card-6.png)

Agent 给我最直观的感受还是提效。真正开始写以后，本地和云端、ReAct 和 Workflow、上下文管理、产品交互都得逐个处理。一个按钮能完成的操作，我个人觉得没必要再套一层 Chat。

![Agent 评测问题](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/9d4d215d_card-7-v2.png)

评测这部分我还没有怎么研究。Bad Case 怎么发现、复现和回归，问题怎么定位到 Prompt、Skill、Tool 或模型，后面都得补上。

#Agent #大语言模型 #AI开发 #Skill #软件工程 #系统设计
