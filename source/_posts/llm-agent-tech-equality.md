---
title: "大模型和Agent正在实现技术平权"
date: 2026-01-10 15:42
tags:
   - 大模型
   - Agent
   - Git
categories:
   - 技术随笔
description: "通过一次Git分支污染事件，探讨大模型和Agent如何实现技术平权，让非专业开发者也能高效解决复杂技术问题。"
---

我对git确实不算了解。

之前校招面试的时候虽然把面试官哄成胎盘，`merge`、`revert`指令在电话中信手拈来。但是不得不说，其实没怎么用过。

工作四年多，只会`pull`、`add`、`commit`、`checkout`、`push`五剑客，复杂的git指令和协作流程日常也没怎么用到，所以工作之后也就没有动力仔细了解过其他复杂的git指令。

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/d951595f_f58e3da3.png)

---

但是常在路边走，哪有不湿鞋。

昨天晚上10点左右，组里一个同事小A像往常一样`commit`、`push`分支需求的代码。但是`push`到测试分支之后，意料之中的发现了冲突——接近年底，不下五个需求分支被合并到了测试分支等待部署到测试环境测试。

这种情况也很常见，小A把测试分支从远程拉了下来，本意是将自己的需求分支合并到测试分支中，但是没想到，一手抖——将测试分支的几百个`commit`全部合并到了自己的需求分支上。

此时小A还没有意识到事情的严重性，或者说他还没有意识到问题，继续在本地的需求分支上提交代码。

当他终于本地提交了几轮，确定本地代码没问题后，准备`push`到远程测试分支的时候，才突然发现，自己的分支已经被测试分支污染了——而他第二天就要提测和发布了，怎么可能将别人的测试分支也发布上线呢？

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/65798b24_d3d68755.png)

---

小A有点慌了。

但是小A和我一样，也对git不算太过了解，折腾了一小时，还是没有把本地的需求分支的污染分支删掉。

没办法，小A基于原来的分支和以前的提交数据，`cherry-pick`了一个新的分支。弄完之后，一看表已经凌晨了，拖着疲惫的身体，踩着月色，小A打了个车，回家了。

事情到此，没有出什么大影响，但是我想，一定有方法将原来分支的垃圾`commit`数据删除，所以第二天一早我打开了GPT。

正当我敲入问题“A分支误`merge`了B分支，如何将B分支的多个`commit`数据删除”，准备按下回车键时，突然想到：“能不能直接让claude帮我操作？”

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/26bf29ab_3e790e50.png)

---

所以就发生了我和claude的如下对话：

我：

> <font style="color:rgba(0, 0, 0, 0.88);">我的git分支不小心merge了其他分支，请帮我回退到commiter=小A，最新一次提交的代码的那次提交</font>
>

CLAUDE：

> <font style="color:rgba(0, 0, 0, 0.88);">收到。我需要先查找“小A”的最新提交哈希，并检查当前工作区的状态。 </font>  
<font style="color:rgba(0, 0, 0, 0.88);">检测到目标提交为 </font><font style="color:rgb(38, 38, 38);background-color:rgba(0, 0, 0, 0.06);">commit_hash_A</font><font style="color:rgba(0, 0, 0, 0.88);">。同时发现当前正处于一个交互式 rebase 操作中，且存在合并冲突。为了安全回退，我需要先中止当前的 rebase，再执行硬重置。</font>
>

我：

> <font style="color:rgba(0, 0, 0, 0.88);">帮我回退到这里：a3a8f43dfa8eac801e804f76cf2c36450c717479</font>
>

CLAUDE：

> <font style="color:rgba(0, 0, 0, 0.88);">没问题，直接将 HEAD 指针重置到该节点。</font>
>

<font style="color:rgba(0, 0, 0, 0.88);">我：</font>

> <font style="color:rgba(0, 0, 0, 0.88);">能帮我把本地分支强制push到远程仓库吗</font>
>

CLAUDE：

> <font style="color:rgba(0, 0, 0, 0.88);">好的，确认当前分支为 </font><font style="color:rgb(38, 38, 38);background-color:rgba(0, 0, 0, 0.06);">feature_1</font><font style="color:rgba(0, 0, 0, 0.88);">。由于刚才进行了回退操作，本地落后于远程，需要执行强制推送。</font>
>

<font style="color:rgba(0, 0, 0, 0.88);">我：</font>

> <font style="color:rgba(0, 0, 0, 0.88);">我发现远程仓库还有之前merge的提交，和我本地的不一样，如何消除？</font>
>

<font style="color:rgba(0, 0, 0, 0.88);">CLAUDE：</font>

> <font style="color:rgba(0, 0, 0, 0.88);">让我对比一下本地 </font><font style="color:rgb(38, 38, 38);background-color:rgba(0, 0, 0, 0.06);">feature_1</font><font style="color:rgba(0, 0, 0, 0.88);"> 和远程分支的提交历史差异。</font>
>
> <font style="color:rgba(0, 0, 0, 0.88);">分析发现：虽然本地指针是对的，但远程历史中包含了大量非线性的 Merge Commit（由构建系统自动产生）。我们需要清理时间线。</font>
>
> <font style="color:rgba(0, 0, 0, 0.88);">请确认你的清洗策略：</font>
>
> 1. **<font style="color:rgba(0, 0, 0, 0.88);">彻底丢弃</font>**<font style="color:rgba(0, 0, 0, 0.88);">目标节点之后的所有提交？</font>
> 2. <font style="color:rgba(0, 0, 0, 0.88);">还是</font>**<font style="color:rgba(0, 0, 0, 0.88);">保留</font>**<font style="color:rgba(0, 0, 0, 0.88);">目标节点后的正常代码提交，仅剔除那些 Merge 节点？</font>
>

我：

> <font style="color:rgba(0, 0, 0, 0.88);">想要保留 a3a8f43dfa 之后的正常提交，只删除那些 merge 提交（非“小A”的提交）</font>
>

<font style="color:rgba(0, 0, 0, 0.88);">CLAUDE：</font>

> <font style="color:rgba(0, 0, 0, 0.88);">明白了。这是一个复杂的“变基清洗”任务。 </font>**<font style="color:rgba(0, 0, 0, 0.88);">策略</font>**<font style="color:rgba(0, 0, 0, 0.88);">：基于干净的节点创建一个临时分支，从旧分支中“捡出（Cherry-pick）”属于小A的有效提交，拼接到新分支上，最后替换原分支。</font>
>
> 1. **<font style="color:rgba(0, 0, 0, 0.88);">创建备份与临时分支</font>**
> 2. **<font style="color:rgba(0, 0, 0, 0.88);">筛选并迁移小A的提交</font>**
> 3. **<font style="color:rgba(0, 0, 0, 0.88);">替换主分支并推送</font>**
>

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/33d938e1_d745243d.png)

---

从给claude提问，到claude完全完成，总共时间不超过十分钟，而且又快又好，那一瞬间，真的让我觉得实现了技术平权。

人们对大模型的应用，不应当只停留在了对话的阶段，通过MCP、RAG各种能力集成的Agent，在prompt得当的时候，真的可以帮我们完成很多事情。

在公司内部，我们也基于大模型和Coder Agent完成了自主的生码能力，同时，很多团队也在积极探索基于大模型和agent的工单自主排查、自主联调等能力。

对于个人用户来讲，也应该利用agent来完成很多琐事的自动处理。在以后，我们的工作范式甚至会发生变化，学会如何和agent说话，如何监控agent可能是一个重要的命题。

在未来，大模型的基础能力很重要，也就是我们常说的pre-training。有的人会说post-training也很重要，这个我不否认，**但是消费市场，agent的能力才是很多人工智能产品决胜的关键**。

我想这也是为什么Meta花费十亿美元收购一家不做model training、只做agent公司的原因，同时，这也是为什么阿里Qwen明明已经全球开源第一了，却也还是干不够豆包的原因之一。

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/5599e669_fb6d2a35.png)

---

最后回到今天的话题，如何快速的把git merge的分支删除呢？请看下图：

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/94da7da8_f317e49c.png)

> 注：本文图片采用Gemini Nano Banana Pro生成
>

