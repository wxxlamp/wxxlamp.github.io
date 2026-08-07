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

正文首图默认采用吉卜力感的温暖手绘动画氛围，比例为 21:9；需要兼容旧文章时可设为 23:9。微信公众号另生成一张带短标题的 2.35:1 封面，正文只对博客版本做轻量排版适配，默认相似度至少 90%。每个一级标题先写视觉 brief，再生成和复审 16:9 配图；小红书轮数由独立主题数决定，每轮先规划 3–9 张 3:4 卡片，常见为 5–7 张。

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

小红书可选接入独立安装的 `XiaohongshuSkills`。插件固定使用其 `--preview` 模式逐轮填充，不自动点击发布，也不把填充成功误报为草稿保存成功：

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
