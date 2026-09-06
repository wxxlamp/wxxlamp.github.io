---
title: "GPT6 Astra使用初体验"
date: 2026-09-06 23:49:03
tags:
  - "AI 编程"
  - "大模型应用"
  - "开发工具"
categories:
  - "场景实践"
description: "花周六一天用Astra改博客、讨论问题、做代码CR，也折腾了15小时视频，聊聊让我惊喜和踩坑的地方。"
---
![周末工程师在窗边检查网页和骑行分镜](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/f2ca3c53_cover.png)

GPT6 Astra发布后，PR满天飞，恰好笔者最近在用Codex做代码开发，来看看是不是真的如传言般厉害。

所以我花了周六一整天来让Astra帮我完成各种任务，直接说结论：“简直amazing”。Astra给我的感觉真的很棒，接下来我就从 Computer Use、视频脚本策划、代码CR、网站制作与UI设计，简单聊下最近一天的使用感受。

# 1. 网站设计与制作

笔者布置给 Astra第一个任务是帮我优化我自己的博客网站：[王星星的魔灯](https://wxxlamp.cn)，提示词如下：

![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/31975fbe_source-01.png)

作为一个审美一言难尽的程序员，我只能给他一个很模糊的提示，让Astra帮我优化网站，这个是一个非常基础的诉求。在等了三十分钟后，Astra给了一个让我惊喜的效果。Astra会自己设计、开发，然后检查，最后通过之后再交付，这种自我检查的效果比我用Sol等模型要好很多。

随后，我又提交了一些其他多语言、布局、文字、SEO等简单的诉求。只需要三言两语，Astra就能迅速get到我的意思，并且完成交付。这在半年前我用Claude Code的时候，是几乎不可能实现的。

![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/4152cda8_source-02.png)

最后展示一下效果，大家可以通过该链接：[博客新旧版对比](https://wxxlamp.cn/design-history/) 看一下原版博客界面和新版博客界面的区别（新版是基于Astra开发、原版是半年前基于Claude Code开发）：

![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/0385b2c0_source-03.png)

![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/9815efa2_source-04.png)

同时，另外一点要提到的是，Astra的审美和理解能力相对于Sol来说，真的是跃升了一大截，包括我本次发布的微信公众号的内容和排版、图片生成，也是Astra自动帮我完成的。

# 2. 问题讨论与开发

同时，因为最近团队的AI业务是基于AgentScope开发的，所以就想看看社区有没有什么issue是自己可以fix的。然后就找到了这个[issue#2373](https://github.com/agentscope-ai/agentscope/issues/2373)。

刚开始看这个issue的时候，肯定是懵逼的，所以我就让Astra快速的帮我理清当前项目的基本模型、数据流等等。

在讨论问题和方案的时候，因为不涉及到代码的开发，Astra给我的反馈就是一个字：“快”。不管我问什么问题，基本两分钟以内就可以给出对应的正确结论：

![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/26c1217d_source-05.png)

甚至在讨论的过程中，我还和Astra发现了另一个 [issue#2522](https://github.com/agentscope-ai/agentscope/issues/2522)，同时Astra还迅速的帮我自动配置，自动复现。真的是大大地节约了我的时间。

不过这里Astra和Sol比较，目前只是觉得Astra体感上优秀一点，并没有在coding上有太超出预期的感觉。

# 3. 代码CR与修复

正好公司最近还有一个cr还没有看，之前用Sol的时候，审查cr改的代码，老是不太符合我的预期，看看Astra怎么样。

由于是公司内部代码，具体的CR内容和修复过程不便展示出来。重点讲下使用Astra的感受：

1. 诉求理解得更精准。在刚开始cr的时候，我提了一些cr的要点和诉求，Astra基本都能理解到，同时还能找出代码的其他兼容性问题；
2. Coding能力目前没有看出来和Sol的区别。只能说明，在复杂的业务场景中，上下文工程可能更加重要，模型能力的提升，并不能带来非常大的收益。
3. 自动化验收的能力会稍强一点。我用简单的提示词提示Astra在开发完代码自动调用接口、通过数据库验收，基本能比较好地遵循我的指令。但是前提还是在于我能把验收规则定义的很清楚才可以；
4. QA环节，速度会比较快。额度消耗上，感觉Astra还是比Sol贵一点。按2026年9月6日的[官方API价格表](https://developers.openai.com/api/docs/pricing)，Standard短上下文的输入、输出单价，Astra都是Sol的2.5倍，不过这个不能直接换算成Pro的额度消耗。

# 4. 视频脚本与分镜

既然 Astra的自我规划、自我监督能力这么强，我能否用一句话，让Astra帮我生成视频呢？

所以我就给Astra发了一段prompt，希望它能帮我生成一个男孩从6到26岁，骑着自行车路过乡间、田野、小学、中学、大学、工作的各个场景。我把我的小学、中学、大学、工作地点告诉了Astra，希望它能自己搜到对应的图片作为背景。

接下来，任务开始：

首先，Astra搜索了不同场景的真实照片，然后生成了不同的关键帧：

![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/b87756de_source-06.png)

然后，Astra使用Blender结合关键帧生成试镜视频。这个时候，Astra会check对应的视频是否符合要求，如果不符合要求，Astra会重新生成。

![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/2ad3d934_source-07.png)

本以为这样就可以美美地生成视频了，但是花费了2亿 token和15个小时之后，发现生成了不少关键帧和短片段，但视频始终没有达到我的预期。这次用下来，Astra更擅长的还是 **规划、组织和检查**，它可以设计分镜、关键帧、检查视频，但是直接让他生成视频，并不是一个好主意（几乎浪费了我Pro一周的额度，多么痛的领悟）。如果强行让Astra生成视频，只会逼得Astra去网上找可以生成视频的小模型，结合Blender，硬生成一些80年代风格的视频。

以下是Astra生成视频的方式

| 阶段 | 实际方法 | 做到了什么 |
| --- | --- | --- |
| 最初的 15 秒版本 | AI 图片＋JavaScript/Canvas 动画 | 完成视频，但人车比例和腿脚不自然 |
| 第二版 | Python 操作 Blender | 建立三维场景和动作，完成部分检查渲染；完整影片未完成 |
| 第三版 | 下载 LTX-2.3 模型，在我的 Mac 上运行 | 生成了若干真实运动的短片段 |
| 74 秒分镜版 | FFmpeg 剪辑 | 主要是图片运镜，加入晨读、办公两个模型生成片段 |

所以我就使用了一个邪修的方式，让Astra通过Computer Use操作浏览器，登录Dreamina，利用账号的免费额度帮我生成。甚至我还让Astra自己帮我去薅羊毛，把能领的额度都领到：

![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/1d5ee885_source-08.png)

但是，可能是prompt的原因，或者是Astra模型能力不支持，Seedance的免费额度不够用，在浪费了大量codex token之后，最后生成的视频不太满意。

# 5. Computer Use

其实上面提到的功能，基本都用到了Computer Use。不得不说，非常好用。这也是Astra主打的一个核心功能。

在开发完个人博客网站后，我希望能提高SEO、以及google分析整体的流量情况，但是我又不知道怎么配置，就给Astra发了一个指令，然后Astra就自动打开了 Google Search Console、Google Analytics，dns服务商网站，来帮我自动配置对应的key、代码，简直不要太方便。要是以前，我最少要操作2小时。

在复现AgentScope Issue的时候，Astra帮我操作了浏览器上的Discord获取bot的密钥、帮我登录GitHub进行issue创建、评论、认领等操作。在代码验证阶段，Astra还操控了浏览器的Discord发送和接收消息。并且它能稳定的识别到浏览器中发生的事情。这和前几个月我用Playwright操控浏览器，有质的差距。

包括本篇文章也会同步让Astra拆分发送到小红书上（小红书地址可以通过我的[博客](https://wxxlamp.cn)获取），打算让Astra自己通过Computer Use功能打开浏览器、进入创作者中心，再把拆分的内容编辑进去。之前在用Sol的时候，这一步老是或多或少有点小问题，现在Astra给我的感觉真的是又快又准。

同时，在剪辑视频的时候，我也是让Astra生成完分镜之后，直接进入浏览器操作Seedance生成的：

![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/78e022ba_source-09.png)

# 6. 用后感

用完Astra之后，给我的感觉真的是牛皮。**它不是说coding能力有了巨大的提升，而是更加接近真实场景，触及到了coding外的其他业务。**

![Astra与Sol：这一天的五类任务体验](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/b0857508_astra-sol-observations.png)

不管是语义理解、审美、电脑操控、token消耗、自我验证、实现速度上，都比Sol进步了不止一个台阶。当然，这些新的能力，不只是Astra的功劳。至于Codex的记忆机制起了多少作用，后续有机会再分析下。

不知不觉，已经用AI工具好几年了。回想自己从2023年到现在使用AI工具的这四年：

<section class="ai-years" style="margin:28px 0;padding:24px 20px 4px;background:#faf5f1;border:1px solid #eadfd7;border-radius:8px;">
<p style="margin:0 0 20px;padding:0 0 0 18px;border-left:3px solid #b58b72;line-height:1.9;"><strong style="display:block;font-size:22px;color:#7a4730;margin:0 0 5px;">23年</strong>使用GPT 3.5 给我自己写的雅思作文打分，以此来省钱；</p>
<p style="margin:0 0 20px;padding:0 0 0 18px;border-left:3px solid #b58b72;line-height:1.9;"><strong style="display:block;font-size:22px;color:#7a4730;margin:0 0 5px;">24年</strong>使用DeepSeek完成论文的翻译，并且辅助我阅读论文、理解代码；</p>
<p style="margin:0 0 20px;padding:0 0 0 18px;border-left:3px solid #b58b72;line-height:1.9;"><strong style="display:block;font-size:22px;color:#7a4730;margin:0 0 5px;">25年</strong>基于Qoder、Cursor、Claude Code完成基本代码的开发（<strong>20%</strong>代码量）、使用Gemini完成学生作业的修改；</p>
<p style="margin:0 0 20px;padding:0 0 0 18px;border-left:3px solid #b58b72;line-height:1.9;"><strong style="display:block;font-size:22px;color:#7a4730;margin:0 0 5px;">26年</strong>使用Codex基本交付了我<strong>95%</strong>的代码开发量，同时，有关电脑的各种复杂操作都会交给Codex来完成。</p>
</section>

可以发现，大模型虽然常被比作成语接龙，但是随着tool use等能力提升，AI已经可以从最开始的问答，慢慢地连接网络世界，完成各种可达性的操作。

最开始使用AI工具的时候，我会优化prompt、控制上下文，以此来让AI实现更好的效果。随着Astra的发布，我发现只需要提供任务，AI会自己完成。不得不说，AI的发展之迅速，远超我的预期。

未来会发展成什么样？很多基础性的工作可能都会被AI替代、可能我也会被替代，但是在替代之前，还是要多看看这个世界呀。
