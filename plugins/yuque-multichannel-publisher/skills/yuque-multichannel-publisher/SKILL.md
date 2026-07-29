---
name: yuque-multichannel-publisher
description: Pull Yuque documents with formatting and re-hosted images, expand and polish incomplete drafts in the repository's established voice, create professional cover/section/social images, and persist resumable Hexo blog, WeChat Official Account, and RedNote publishing packages. Use when a user provides a yuque.com document, asks to turn a draft or outline into publishable multi-channel content, wants blog/微信公众号/小红书 variants, or wants to resume a content project from its local .codex checkpoint.
---

# 语雀多平台发布

把一篇语雀文档加工成三个平台的发布包。本插件只有当前一个主 Skill；语雀拉取、图床上传、语气缓存和持久化都是 `scripts/` 中的内部组件，不依赖工作区 `.agents/skills`。

默认以 `content-projects/<slug>/` 为内容项目，所有阶段状态原子化写入该项目的 `.codex/`，因此必须先读取状态再继续，不能凭对话记忆猜测进度。

## 开始前

1. 从当前目录向上寻找工作区。无法自动识别时设置 `YMP_WORKSPACE_ROOT=/absolute/project/path`。
2. 首次使用或配置图床时阅读 [configuration.md](references/configuration.md)。润色前阅读 [style-profile-cache.md](references/style-profile-cache.md) 和 [editorial-guide.md](references/editorial-guide.md)。需要生成三端产物时，再阅读 [artifact-contract.md](references/artifact-contract.md)；需要代发时，再阅读 [publishing.md](references/publishing.md)。
3. 使用本技能的 `scripts/pipeline.py` 管理项目。不要手工修改 `.codex/state.json`。
4. 首次使用时安装本 Skill 的 `requirements.txt`，并执行 `playwright install chromium`。
5. 将语雀登录态、语气档案和图床配置留在工作区 `.codex/yuque-multichannel-publisher/` 或环境变量中，绝不写入插件目录。

初始化工作区配置：

```bash
python3 plugins/yuque-multichannel-publisher/skills/yuque-multichannel-publisher/scripts/pipeline.py setup
```

默认目录可以用 `setup` 参数覆盖，也可以编辑生成的 `.codex/yuque-multichannel-publisher/config.json`。脚本入口：

```bash
python3 plugins/yuque-multichannel-publisher/skills/yuque-multichannel-publisher/scripts/pipeline.py --help
```

## 工作流

### 1. 新建或恢复项目

新任务：

```bash
python3 <pipeline.py> init \
  --project <english-slug> \
  --yuque-url <url> \
  --title "<标题>"
```

恢复任务：

```bash
python3 <pipeline.py> resume --project <english-slug>
```

每完成一个需要 AI 判断的阶段，都执行：

```bash
python3 <pipeline.py> checkpoint \
  --project <english-slug> \
  --stage <polished|illustrated|reviewed> \
  --artifact <path> \
  --note "<完成内容>"
```

### 2. 拉取语雀正文和原图

执行：

```bash
python3 <pipeline.py> fetch --project <english-slug>
```

这会调用插件内部的 `scripts/yuque_fetcher.py`，把 Markdown 写入项目的 `raw/source.md`，并通过内部 `scripts/image_uploader.py` 迁移原图。登录失效时加 `--login`。不得把拉取失败误记为完成。

### 3. 学习语气并润色

先检查分类语气缓存：

```bash
python3 plugins/yuque-multichannel-publisher/skills/yuque-multichannel-publisher/scripts/style_profiles.py \
  prepare --category "<分类>"
```

严格按照输出执行：

- `reuse`：只读取已有语气档案，不读取任何样本文章。
- `learn`：AI 首次阅读返回的 3–8 篇样本，提炼并保存紧凑语气档案。
- `refresh`：AI 读取旧档案、变化文章和最多两篇锚点文章，增量更新；禁止扫描整个分类。
- `blocked`：尝试 `default` 档案；仍无缓存时使用克制的默认语气。

语气特征提炼、内容润色和扩写必须由 AI 完成。脚本只能管理指纹与缓存，不能分析语言或改写正文。不要加载工作区中其他语言分析缓存；紧凑语气档案是唯一常规语气上下文。

允许把骨架扩展为完整文章，但不得虚构经历、数据、引用、结论或已验证结果。把成稿写入 `draft/polished.md`，元数据写入 `metadata.json`，然后记录 `polished` 检查点。

### 4. 生成、上传并插入配图

使用可用的图片生成工具：

- 开篇封面：专业、克制、无水印、尽量无文字，比例严格为 23:9。
- 每个一级标题：紧随标题放置一张语义相关的专业图片，比例严格为 16:9。
- 小红书：每轮至少一张竖版或 3:4 信息卡；封面标题控制在 12 个汉字以内。
- 同一项目共享色板、光线、材质和构图语言，不共享完全相同的画面。

把本地图片保存到 `content-projects/<slug>/images/`，再上传：

```bash
python3 <pipeline.py> upload-image \
  --project <english-slug> \
  --kind <cover|section|rednote> \
  --key "<标题或round1>" \
  --file <local-image> \
  --provider <imgur|smms|github|chevereto>
```

脚本会调用插件内部图片上传模块、解析远程 URL 并写入 `metadata.json`。把远程 URL 插入三端 Markdown，成功后记录 `illustrated` 检查点。

### 5. 改写三端内容

- 博客：保留完整论证、代码、引用与目录结构，正文源为 `draft/polished.md`。
- 微信：AI 同时写入 `draft/wechat.md` 和已经排好版的 `draft/wechat.html`。以手机阅读为目标，段落更短、转场更显式、代码块保持完整；HTML 使用行内样式，不依赖脚本二次排版。
- 小红书：写入 `draft/rednote/round1/post.md`、`round2/post.md`……。按独立主题拆分，不把长文机械截断；每轮包含标题、正文、配图链接、话题标签与下一轮衔接。

遵守 [artifact-contract.md](references/artifact-contract.md) 后执行：

```bash
python3 <pipeline.py> validate --project <english-slug> --phase draft
python3 <pipeline.py> materialize --project <english-slug>
python3 <pipeline.py> validate --project <english-slug> --phase materialized
```

`materialize` 默认生成以下文件；实际根目录以工作区配置为准：

- `source/_posts/<slug>.md`
- `wechat/<slug>/article.md`
- `wechat/<slug>/article.html`（适合浏览器打开后复制到公众号编辑器）
- `rednote/<slug>/roundN/post.md`

### 6. 审阅与发布

先记录 `reviewed` 检查点。只有在用户明确要求发布时，才按 [publishing.md](references/publishing.md) 使用已登录浏览器：

1. 优先保存到平台草稿箱。
2. 保存草稿后记录平台、草稿标识或可见标题。
3. 在最终“发布/群发”动作前展示标题、账号、可见范围和计划时间。
4. 只有用户明确确认最终动作后才能点击发布。
5. 每个平台独立记录成功或失败，失败不得回滚本地产物。

## 质量闸门

- 不遗漏语雀原有格式、代码块、链接和图片。
- 开篇有 23:9 封面；每个一级标题有 16:9 图片。
- 博客语气与对应分类的历史文章一致，但不刻意复制句子。
- 语气缓存命中时不重读样本；缓存失效时只做增量刷新。
- 微信 HTML 不依赖外部 CSS；图片均使用可公开访问的 HTTPS URL。
- 小红书每轮可独立发布，避免“见上文”式依赖，并避免未经验证的绝对化表达。
- `validate` 无错误后才进入平台草稿；平台草稿完成不等于已发布。

## 可选平台能力

润色、语气仿写、图片策划、图片生成、微信排版和小红书改写由 AI 完成。图片生成需要当前 Codex 环境具备图片生成能力；浏览器代发需要浏览器控制能力。缺少这些可选能力时，仍可完成语雀拉取、AI 文本加工、本地持久化与校验。
