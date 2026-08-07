# 一篇长文，三端发布

![一篇长文生成三端发布包](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/1590fedc_card-1.png)

如果你习惯在语雀写长文，还要同步到个人博客、微信公众号和小红书，这个 Codex Plugin 就是为这段重复流程做的。我的核心判断很简单：需要理解上下文的工作交给 AI，结果明确的操作交给脚本，再用检查点把长任务保存下来。

过去每篇文章写完，我还要为三个平台分别排版、配图、拆文和检查，一轮大约多花两个小时。后来我把语雀读取、语气润色、图片策划、三端改写、上传和校验收进一个自包含插件。

![三端分发的重复工作与时间成本](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/4b1435fa_card-2.png)

这里最关键的是分工：AI 负责语气、内容补充、视觉 brief 和渠道改写；脚本负责下载、上传、图片比例、目录、相似度和状态记录。AI 可以发挥，但要留下可检查的产物；脚本只验证明确规则，不偷偷改正文。

![AI 与脚本的职责分工](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/5df40603_card-3.png)

长任务中断也不用重来。每个项目都会保存原文、草稿、图片、哈希和检查点，恢复时能直接看到上次做到哪里。最终产物包括完整的 Hexo 博客文章、公众号 Markdown/HTML 与独立封面，以及一篇可独立阅读的小红书笔记和 5 张卡片。

![检查点让长任务中断后继续](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/eb2d3e3a_card-4.png)

这个版本仍有边界：图床需要自己配置凭据，公众号和小红书的最终发布依赖已登录的浏览器，真正发布前仍要确认账号、标题、时间和可见范围。

![三端产物与可检查的质量证据](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/966f0bc8_card-5.png)

插件源码和使用说明：github.com/wxxlamp/ai-coding-config

你在多平台发布时，最想先省掉哪一步？

#Codex #内容创作 #效率工具 #公众号排版 #小红书运营 #个人博客 #自动化工作流
