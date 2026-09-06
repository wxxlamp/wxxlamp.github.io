# 语雀多平台发布插件

一个自包含的 Codex Plugin：从语雀读取 Markdown 和原图，由 AI 完成润色、语气匹配、去 AI 味复审、配图、微信公众号排版及小红书改写，再由插件脚本完成图床上传、断点记录、质量检查、三端落盘和可选草稿适配。

插件不依赖目标仓库的 `.agents/skills`。复制整个 `yuque-multichannel-publisher/` 目录即可分发；用户配置、登录态、个人语气档案和任务进度保存在目标工作区 `.codex/yuque-multichannel-publisher/`，不会随插件复制。

插件里只有通用的语气学习规范。第一次使用时，AI 会读取当前用户的历史文章，将个人语气基线保存到工作区 `style-profiles/author-voice.md`；以后按语料指纹复用或增量刷新。插件不会生成图床或平台密钥，用户必须通过环境变量、工作区配置或浏览器登录提供凭据。

## 第一次使用

```bash
python3 -m pip install -r skills/yuque-multichannel-publisher/requirements.txt
python3 skills/yuque-multichannel-publisher/scripts/pipeline.py setup
```

在工作区 `.codex/yuque-multichannel-publisher/config.json` 中配置图床。支持 Imgur、SM.MS、GitHub 和 Chevereto，凭据也可以通过环境变量提供。

## 在 Codex 中使用

直接发送自然语言即可：

```text
使用 yuque-multichannel-publisher，把这篇语雀文档加工为博客、公众号和小红书发布包：<URL>。
使用补充润色模式，先生成平台草稿，不要直接发布。
```

也可以只选部分平台或只纠错：

```text
使用 yuque-multichannel-publisher，只纠正这篇语雀文章的错别字和病句，生成博客与公众号版本，不要扩写，也不要生成小红书。
```

正文首图默认采用吉卜力感的温暖手绘动画氛围，比例为 21:9；需要兼容旧文章时可设为 23:9。微信公众号另生成一张带短标题的 2.35:1 封面，正文只对博客版本做轻量排版适配，默认相似度至少 90%。按解释需要选择章节配图，先写视觉 brief 与位置理由，再生成和复审 16:9 图片；小红书轮数由独立主题数决定，每轮先规划 3–9 张 3:4 卡片，常见为 5–7 张。

`content-projects/<slug>/` 是可恢复的草稿和进度目录，不是最终发布目录。AI review 通过并执行 `materialize` 后，最终文件才会进入：

- 博客：`source/_posts/<slug>.md`
- 微信公众号：`wechat/<slug>/article.md` 和 `article.html`
- 小红书：`rednote/<slug>/series-plan.json`、每轮的 `post.md` 与 `cards.json`；轮数由内容决定，不固定为三轮

## 恢复任务

```bash
python3 skills/yuque-multichannel-publisher/scripts/pipeline.py resume --project <slug>
```

`content-projects/<slug>/.codex/state.json` 是任务进度真相。不要手工改状态文件。

## 发布就绪检查与平台草稿

先用一条命令查看内容质量、三端产物和适配器状态：

```bash
python3 skills/yuque-multichannel-publisher/scripts/pipeline.py inspect \
  --project <slug> --probe
```

微信公众号可选接入独立安装的 `md2wechat`。配置好其凭据和本插件的可执行文件路径后，可先检查再写入官方草稿箱：

```bash
python3 skills/yuque-multichannel-publisher/scripts/pipeline.py send-draft \
  --project <slug> --channel wechat --confirm
```

投递会直接复用已经物化的 `article.html`，上传既有封面和正文图片后调用微信草稿 API，不需要再次转换或生成文章。成功素材会缓存在项目 `.codex/`，只有取得草稿 `media_id` 才记录为已保存。

小红书发布优先复用 Codex 当前已打开、已登录的浏览器和现有标签页。只有当前浏览器无法控制且用户明确同意 CLI 回退时，才接入独立安装的 `XiaohongshuSkills`。回退流程固定使用其 `--preview --reuse-existing-tab` 模式，默认禁止在没有现成 CDP 会话时新开 Chrome，也不自动点击发布或把填充成功误报为草稿保存成功：

```bash
python3 skills/yuque-multichannel-publisher/scripts/pipeline.py send-draft \
  --project <slug> --channel rednote --round round1 --confirm
```

平台页面确认保存后，再用 `record-delivery --status draft_saved` 记录。公众号、小红书以及每个小红书轮次的状态彼此独立。

## 本地开发更新

修改插件后执行：

```bash
python3 <plugin-creator-skill>/scripts/update_plugin_cachebuster.py \
  /absolute/path/to/yuque-multichannel-publisher

python3 <plugin-creator-skill>/scripts/validate_plugin.py \
  /absolute/path/to/yuque-multichannel-publisher

codex plugin add yuque-multichannel-publisher@<marketplace-name>
```

重新安装后，新建一个 Codex 任务以加载新版插件。

## 编辑与排版 v2

新项目按读者问题和原文材料规划小红书篇数，每篇有独立收益与素材映射。语气学习使用有指纹的作者基线，自动排除已知流水线成稿；博客、微信、小红书正文与卡片逐项检查语气、错字、格式和事实。复审与文件 SHA-256 绑定，内容改动后重新审阅。

微信提供 `wechat_layout.py` 的 ink/warm 两种行内样式，以及 `wechat_preview.py` 的 375px/430px 预览。默认取消每个标题后强制配图。知识核查与审美判断仍由 AI 实际完成，脚本只检查结构、保真和复审是否过期，不把形式检查冒充内容质量保证。

升级后在使用的 Python 环境安装 Skill 的 requirements.txt。新建项目自动启用 v2；旧项目按 references/editorial-review.md 迁移，原有产物和投递记录保留。


## 标题、分类和英文版

博客使用专业清晰的独立标题，公众号、小红书按真实读者收益选择更有吸引力的标题。新项目通过 `publishing-context` 读取当前博客分类话题目录，由 AI 根据专业深度决定英文版；面试与零散备忘通常跳过。选中的文章完整翻译并生成英文配图，写入 `source/_posts/en/`，保留双语对应关系。

发布决策和英文稿纳入 SHA-256 复审，阻止未知标签、未审阅英文图片和修改后未复核的材料进入成品。旧项目保持兼容；详见 [发布计划契约](skills/yuque-multichannel-publisher/references/publishing-plan.md)。


引用也按正文语言匹配：读取真实双语文章路由，检查旧地址、缺失译文与引用锚点，外部资料使用核验过的同源译文。不存在对应语言的原始来源需明确标注语言；不伪造 `/en/` 页面。引用复审纳入发布计划指纹，支持 Markdown、HTML 与裸链接，保持代码和图片不变。
