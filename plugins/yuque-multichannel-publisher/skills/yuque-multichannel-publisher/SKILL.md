---
name: yuque-multichannel-publisher
description: Pull Yuque documents with formatting and re-hosted images, expand and polish incomplete drafts in the repository's established voice, create professional cover/section/social images, persist resumable Hexo blog, WeChat Official Account, and RedNote packages, inspect publishing readiness, and optionally send content through external draft adapters. Use when a user provides a yuque.com document, asks to turn a draft or outline into publishable multi-channel content, wants blog/微信公众号/小红书 variants or drafts, or wants to resume a content project from its local .codex checkpoint.
---

# 语雀多平台发布

把一篇语雀文档加工成三个平台的发布包。本插件只有当前一个主 Skill；语雀拉取、图床上传、语气缓存和持久化都是 `scripts/` 中的内部组件，不依赖工作区 `.agents/skills`。

默认以 `content-projects/<slug>/` 为内容项目，所有阶段状态原子化写入该项目的 `.codex/`，因此必须先读取状态再继续，不能凭对话记忆猜测进度。

## 开始前

1. 从当前目录向上寻找工作区。无法自动识别时设置 `YMP_WORKSPACE_ROOT=/absolute/project/path`。
2. 首次使用或配置图床时阅读 [configuration.md](references/configuration.md)。润色前阅读 [voice-profile.md](references/voice-profile.md)、[style-profile-cache.md](references/style-profile-cache.md) 和 [editorial-guide.md](references/editorial-guide.md)，再读取工作区 `.codex/yuque-multichannel-publisher/style-profiles/author-voice.md`；缺少该文件时，先由 AI 基于当前用户的历史文章创建。生成图片前必须阅读 [visual-direction.md](references/visual-direction.md)。需要生成三端产物时，再阅读 [artifact-contract.md](references/artifact-contract.md)；需要代发时，再阅读 [publishing.md](references/publishing.md)。
3. 使用本技能的 `scripts/pipeline.py` 管理项目。不要手工修改 `.codex/state.json`。
4. 首次使用语雀兼容拉取器时安装本 Skill 的 `requirements.txt`，并执行 `playwright install chromium`。平台发布适配器是可选外部依赖，不能复制进插件或代替用户配置账号。
5. 将语雀登录态、个人语气档案和图床配置留在工作区 `.codex/yuque-multichannel-publisher/` 或环境变量中，绝不写入插件目录。插件不会创建、猜测或自动申请任何密钥；缺少凭据时提示用户自行配置。

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
  --title "<标题>" \
  --edit-mode <correction-only|polish-expand> \
  --channels <blog wechat rednote>
```

- `correction-only`：AI 只修正错别字、病句、标点和明显格式问题，不扩展观点。
- `polish-expand`：AI 在相同事实边界内补充背景、转场、例子和限制条件。
- `--channels` 可只选一个或两个平台；未选择的平台不生成、不校验，也不发布。

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

首选当前 Codex 环境提供的 Browser Controller，因为非语雀会员、私有文档或接口策略变化时，内部接口可能不可用：

1. 在用户已登录语雀的浏览器中打开文档，确认页面标题与 URL。
2. 优先使用页面“复制为 Markdown”能力；如果浏览器无法读取复制结果，则从可见文章容器提取标题层级、段落、列表、引用、代码、链接和图片，AI 保真转换为 Markdown。
3. 把浏览器导出的内容写入临时 Markdown，再交给插件记录状态：

```bash
python3 <pipeline.py> ingest \
  --project <english-slug> \
  --input <browser-export.md> \
  --title "<页面标题>" \
  --migrate-images
```

`--migrate-images` 会调用插件内置图床模块迁移语雀原图。原文没有图片时可以省略。

只有 Browser Controller 不可用、且文档允许接口读取时，才使用兼容回退命令：

执行：

```bash
python3 <pipeline.py> fetch --project <english-slug>
```

这会调用插件内部的 `scripts/yuque_fetcher.py`，把 Markdown 写入项目的 `raw/source.md`，并通过内部 `scripts/image_uploader.py` 迁移原图。不得把 401、空正文或图片迁移失败误记为完成。

### 3. 学习语气并润色

先读取工作区 `.codex/yuque-multichannel-publisher/style-profiles/author-voice.md`。如果不存在，AI 首次读取当前用户的历史文章，按照 `references/voice-profile.md` 生成紧凑基线并写入工作区。语料指纹没有变化时，不得重读全部文章。个人语气不会进入插件包。

需要更细的分类差异时，再检查分类语气缓存：

```bash
python3 plugins/yuque-multichannel-publisher/skills/yuque-multichannel-publisher/scripts/style_profiles.py \
  prepare --category "<分类>"
```

严格按照输出执行：

- `reuse`：只读取已有语气档案，不读取任何样本文章。
- `learn`：AI 首次阅读返回的 3–8 篇样本，提炼并保存紧凑语气档案。
- `refresh`：AI 读取旧档案、变化文章和最多两篇锚点文章，增量更新；禁止扫描整个分类。
- `blocked`：尝试 `default` 档案；仍无缓存时使用克制的默认语气。

语气特征提炼、内容润色和扩写必须由 AI 完成。脚本只能管理指纹与缓存，不能分析语言或改写正文。工作区作者基线加可选的分类档案是唯一常规语气上下文。

根据 `metadata.json` 的 `edit_mode` 执行对应强度。`correction-only` 不得新增论点和段落；`polish-expand` 允许把骨架扩展为完整文章，但不得虚构经历、数据、引用、结论或已验证结果。所有 `#` 标题使用 `1. 标题`，`##` 使用 `1.1. 标题`，更深层级依次编号。

`polish-expand` 必须再执行一次由 AI 完成的“去 AI 味”复审：删除模板化时代开场、空泛黑话、机械转场、过密排比、重复总结和夸大结论；尤其检查高频的“不是……而是……”“不只是……更是……”否定对照句。打散过于整齐的句长与段落节奏，保留作者真实的一人称判断、具体细节、犹豫和边界。不能为了口语化添加虚假经历、网络梗或滥用 emoji。完成后在 `metadata.json.ai_tone_review` 记录 `status: passed`、作者基线指纹、全部检查项和简短说明，再把成稿写入 `draft/polished.md` 并记录 `polished` 检查点。具体遵守 [editorial-guide.md](references/editorial-guide.md)。

### 4. 生成、上传并插入配图

先按 [visual-direction.md](references/visual-direction.md) 为每个图片槽位写 brief，再使用可用的图片生成工具。生成后 AI 必须实际查看图片并记录 review；图片文件存在或比例正确，不代表语义合格。

- 正文首图：默认比例为 21:9，可配置为 23:9；视觉上优先采用吉卜力感的温暖手绘动画氛围，但不得复刻具体角色、场景或受保护元素。
- 微信公众号封面：与正文首图分开生成和记录，比例严格为 2.35:1；延续合适的画面风格，在安全留白区加入 8–14 字短标题，并逐字复核。
- 每个一级标题：紧随标题放置一张语义相关的专业图片，比例严格为 16:9；图片必须表现 brief 的 `section_claim` 与 `must_show`，不能用泛化办公桌、抽象卡片或发光 AI 芯片代替内容。
- 小红书：每轮 3–9 张 3:4 卡片，常见为 5–7 张；先规划卡片叙事，封面标题控制在 12 个汉字以内。
- 所有图片保持专业完成度和信息准确性，但不要求共享同一色板或材质；优先让风格服务于内容。

把本地图片保存到 `content-projects/<slug>/images/`，再上传：

```bash
python3 <pipeline.py> upload-image \
  --project <english-slug> \
  --kind <cover|wechat-cover|section|rednote> \
  --key "<标题或round1>" \
  --file <local-image> \
  --provider <imgur|smms|github|chevereto>
```

`cover` 是正文首图，`wechat-cover` 是微信公众号后台封面字段。脚本会校验实际比例、调用插件内部图片上传模块、解析远程 URL 并写入 `metadata.json`。把正文图片的远程 URL 插入三端 Markdown；微信封面不插入正文，由发布阶段单独填写。成功后记录 `illustrated` 检查点。

### 5. 改写三端内容

- 博客：保留完整论证、代码、引用与目录结构，正文源为 `draft/polished.md`。
- 微信：AI 同时写入 `draft/wechat.md` 和已经排好版的 `draft/wechat.html`。`wechat.md` 以博客正文为唯一内容底稿，默认保留全部观点、事实、章节、代码和图片，只允许拆短段落、调整极少量平台称呼或在结尾增加一句互动；不得摘要化、重组论证或另写一篇。流水线默认要求其与博客正文相似度至少 90%。`wechat.html` 只做行内样式排版，文本语义必须与 `wechat.md` 一致。
- 小红书：先提取原文的对象、目标读者、核心判断、可执行信息和真实材料，再判断能支撑几篇无需前文也能读懂的笔记。同一产品介绍所需的动机、做法和结果通常应留在一篇，不能按长文章章节拆轮；只有主题、读者收益和证据材料都能独立成立时才增加轮次。每轮先写 `series-plan.json` 中的完整上下文，再写 `cards.json` 规划 3–9 张卡片，最后生成独立可读的 `post.md`。开头 120 个可见字符内重新点明对象、目标读者与核心观点，禁止“上一轮、下一轮、上文、前文、见前”等依赖。图片优先使用真实截图和材料，单卡只推进一个信息点。

完成三个草稿后，AI 必须做一次内容 review：检查事实边界、错别字、标题编号、图片语义、三端差异、发布字段和是否残留明显 AI 腔，再记录 `reviewed` 检查点。没有 `reviewed` 检查点时，`materialize` 默认拒绝分发。

遵守 [artifact-contract.md](references/artifact-contract.md) 后执行：

```bash
python3 <pipeline.py> validate --project <english-slug> --phase draft
python3 <pipeline.py> materialize --project <english-slug>
python3 <pipeline.py> validate --project <english-slug> --phase materialized
python3 <pipeline.py> inspect --project <english-slug>
```

`content-projects/<slug>/` 只是可恢复的工作草稿区，不是最终发布目录。只有 `reviewed` 后执行 `materialize`，才算完成持久化。命令默认生成以下最终文件；实际根目录以工作区配置为准：

- `source/_posts/<slug>.md`
- `wechat/<slug>/article.md`
- `wechat/<slug>/article.html`（适合浏览器打开后复制到公众号编辑器）
- `rednote/<slug>/roundN/post.md`
- `rednote/<slug>/roundN/cards.json`
- `rednote/<slug>/series-plan.json`

只生成 `metadata.json.channels` 选中的平台；例如仅选择 `blog wechat` 时，小红书文件不是必需产物。

### 6. 审阅与发布

先记录 `reviewed` 检查点并执行 `inspect`。只有在用户明确要求操作外部平台时，才按 [publishing.md](references/publishing.md) 使用外部适配器或已登录浏览器：

1. 博客可在用户明确要求时执行 Git commit；是否 push 必须遵守目标仓库规则。本仓库禁止 Codex push，因此只能交给用户手工 push。
2. 微信可选用 `md2wechat`：必须先 `inspect --probe`，再执行带 `--confirm` 的 `send-draft --channel wechat`。默认复用已物化的 `article.html`，上传既有封面与正文图片并调用 `create_draft`；不因缺少转换 API Key 重新生成正文。只有返回草稿 `media_id` 后才记录 `draft_saved`。
3. 小红书可选用 `XiaohongshuSkills`：`send-draft --channel rednote --round roundN` 固定使用 `--preview`，只记录 `filled_for_review`；平台明确提示保存成功后，再用 `record-delivery` 记录 `draft_saved`。
4. `filled_for_review`、`draft_saved` 与 `published` 是三个不同状态，禁止互相替代。公众号、小红书及每个小红书轮次都独立记录。
5. 在最终“发布/群发”动作前展示标题、账号、可见范围和计划时间；只有用户明确确认后才能点击。
6. 每个平台独立记录成功或失败，失败不得回滚本地产物，也不得把整个项目的内容阶段倒退。

## 质量闸门

- 不遗漏语雀原有格式、代码块、链接和图片。
- 正文开篇有配置指定的 21:9 或 23:9 吉卜力感首图；微信渠道另有 2.35:1 封面；每个一级标题有内容驱动的 16:9 图片。
- 所有标题按层级编号；`correction-only` 不得发生内容扩写。
- 博客语气与对应分类的历史文章一致，但不刻意复制句子。
- `polish-expand` 已完成去 AI 味复审；没有模板化开场、机械总结、空泛排比和连续同节奏段落，也没有为了“像人”而编造经历。
- 语气缓存命中时不重读样本；缓存失效时只做增量刷新。
- 微信 HTML 不依赖外部 CSS；图片均使用可公开访问的 HTTPS URL。
- 小红书轮数由 AI 根据独立主题数决定，实际 roundN 必须与系列计划一致；每轮开头重建上下文，包含 3–9 张卡片、明确钩子、互动问题和 5–8 个标签，不使用跨轮指代。
- `validate` 无错误后才进入平台草稿；平台草稿完成不等于已发布。
- `inspect.targets.*.blockers` 是发布就绪事实来源；`resume.next_actions` 按渠道给出后续动作，不再把三端压成一个线性 `drafted` 阶段。

## 可选平台能力

润色、语气仿写、图片策划、图片生成、微信排版和小红书改写由 AI 完成。图片生成需要当前 Codex 环境具备图片生成能力。微信公众号可通过用户单独安装并配置的 `md2wechat` 写入草稿箱；小红书参考适配器只验证到预览填充，服务器草稿仍需在已登录页面确认。缺少适配器或浏览器控制能力时，仍可完成语雀拉取、AI 文本加工、本地持久化、质量报告与发布包交付。
