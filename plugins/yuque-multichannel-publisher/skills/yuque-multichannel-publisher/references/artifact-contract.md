# 产物契约

## 工作区本地状态

```text
<workspace>/.codex/yuque-multichannel-publisher/
├── config.json
├── browser-data/storage_state.json
└── style-profiles/
    ├── profile-index.json
    └── style-*.json
```

该目录包含配置、登录态、`style-profiles/author-voice.md` 和分类语气档案，不得打包进插件或提交到公共仓库。插件只携带 `references/voice-profile.md` 通用规范，不携带任何作者的个人语气。

## 内容项目目录

```text
content-projects/<slug>/
├── .codex/
│   ├── state.json
│   └── events.jsonl
├── metadata.json
├── raw/
│   └── source.md
├── draft/
│   ├── polished.md
│   ├── wechat.md
│   ├── wechat.html
│   └── rednote/
│       ├── series-plan.json
│       ├── round1/
│       │   ├── post.md
│       │   └── cards.json
│       ├── round2/
│       │   ├── post.md
│       │   └── cards.json
│       └── ...
└── images/
```

`.codex/state.json` 由脚本原子更新，是恢复任务的唯一进度真相。`events.jsonl` 是追加式审计日志。不要把登录 cookie、API token 或浏览器存储复制进项目。

微信公众号素材上传成功后，可在 `.codex/wechat-materials.json` 缓存文件哈希、`media_id` 和微信素材 URL，以便草稿创建中断后复用。缓存不得包含 AppSecret、access token 或完整适配器错误响应。

内容处理阶段止于 `persisted`。平台投递不再改写统一的 `current_stage`，而是按渠道和小红书轮次写入 `deliveries`：

```json
{
  "current_stage": "persisted",
  "deliveries": {
    "wechat": {
      "article": {"status": "draft_saved", "account": "account-alias"}
    },
    "rednote": {
      "round1": {"status": "filled_for_review", "account": "account-alias"}
    }
  }
}
```

允许的投递状态是 `filled_for_review`、`draft_saved`、`published` 和 `failed`。账号字段只保存外部适配器别名，不保存登录凭据。

## metadata.json

旧版 metadata 核心字段示例如下；v2 新增字段与统一编辑复审见文末，不必填写旧版 ai_tone_review：

```json
{
  "project": "english-slug",
  "yuque_url": "https://www.yuque.com/...",
  "title": "文章标题",
  "edit_mode": "polish-expand",
  "channels": ["blog", "wechat", "rednote"],
  "cover_ratio": "21:9",
  "wechat_cover_ratio": "2.35:1",
  "lead_image_style": "ghibli-inspired",
  "wechat_similarity_min": 0.9,
  "ai_tone_review": {
    "status": "passed",
    "voice_reference": ".codex/yuque-multichannel-publisher/style-profiles/author-voice.md",
    "corpus_fingerprint": "0000000000000000000000000000000000000000000000000000000000000000",
    "checks": [
      "template_opening",
      "empty_abstractions",
      "mechanical_transitions",
      "negative_parallelism",
      "rule_of_three",
      "excessive_parallelism",
      "repetitive_summaries",
      "generic_conclusion",
      "manufactured_punchline",
      "inflated_claims",
      "uniform_sentence_rhythm",
      "vague_attribution",
      "chatbot_artifacts"
    ],
    "notes": "AI 根据语气档案完成二次复审，无需脚本改写正文。"
  },
  "description": "40–60 字描述",
  "tags": ["标签"],
  "categories": ["分类"],
  "cover_image": {
    "url": "https://...",
    "local": "content-projects/.../images/cover.png",
    "ratio": "21:9",
    "style": "ghibli-inspired"
  },
  "wechat_cover_image": {
    "url": "https://...",
    "local": "content-projects/.../images/wechat-cover.png",
    "ratio": "2.35:1",
    "title": "我把内容分发做成插件",
    "title_safe_area": "left-center",
    "review_status": "passed"
  },
  "section_images": {
    "flow-overview": {
      "section": "1. 处理流程",
      "placement_reason": "放在整体流程说明之后，帮助读者串联后续步骤",
      "url": "https://...",
      "local": "...",
      "ratio": "16:9",
      "section_claim": "本节要说明的一句话",
      "visual_type": "process-diagram",
      "must_show": ["对象 A", "对象 B", "两者关系"],
      "avoid": ["无关办公桌", "错误代码"],
      "prompt": "实际使用的完整生图提示词",
      "review_status": "passed"
    }
  },
  "rednote_images": {
    "round1": []
  }
}
```

目录名均可在工作区 `config.json` 中覆盖。

## 博客

- 目标：`source/_posts/<slug>.md`
- 仅在 `channels` 包含 `blog` 时生成。front matter 由脚本生成，包含 `title`、`date`、`tags`、`categories`、`description`。
- 正文保持长文完整度和 Hexo Markdown 兼容性。

## 微信公众号

- 仅在 `channels` 包含 `wechat` 时生成。目标：`wechat/<slug>/article.md` 与 `article.html`。
- Markdown 不含 Hexo front matter。
- Markdown 与博客正文基本一致，默认相似度不得低于 90%；只做段落级轻适配，不删减或重写主体内容。
- HTML 由 AI 设计，可使用内置 wechat_layout.py 渲染行内样式，使用行内样式，不加载脚本或外部 CSS；物化流水线只复制和校验，不得重新排版。
- 发布时从 `wechat_cover_image` 读取独立的 2.35:1 微信封面，不把它当作正文第一张图。
- 实际粘贴后仍需检查代码块、表格、图片宽度和公众号编辑器的二次清洗。

## 小红书

- 仅在 `channels` 包含 `rednote` 时生成。目标：`rednote/<slug>/series-plan.json`、`roundN/post.md` 与 `roundN/cards.json`。
- 轮数由 AI 根据内容密度和独立主题决定，可以只有 round1，也可以有多个连续轮次。`series-plan.json` 必须记录 `round_count_reason`；每轮必须有唯一的 `angle`，并与实际目录一一对应。
- 每轮建议 300–900 个可见字符，硬上限由发布时的平台规则决定。
- 每轮必须能够独立理解，开头 120 个可见字符内交代对象、目标读者和核心观点，并包含一个明确标题、互动问题、3–9 张卡片和 5–8 个相关话题标签。
- 同一事实不在多轮中重复堆砌；禁止依靠“上一轮、下一轮、上文、前文、见前”等跨轮指代维系理解。

`series-plan.json` 的最小结构：

```json
{
  "series_title": "系列标题",
  "round_count_reason": "AI 为什么把本文规划为当前轮数",
  "rounds": [
    {
      "round": "round1",
      "angle": "本轮独立角度",
      "subject": "本轮讨论的明确对象",
      "target_reader": "目标读者",
      "core_viewpoint": "离开其他轮仍成立的核心判断",
      "context_brief": "本轮开头必须重新交代的必要背景",
      "reader_promise": "读者读完得到什么",
      "hook": "开头钩子",
      "image_plan": ["首图", "步骤图", "结论图"]
    }
  ]
}
```

每个 `roundN/cards.json` 的最小结构：

```json
{
  "cards": [
    {
      "index": 1,
      "role": "cover",
      "headline": "12 字以内的主题",
      "body": "单卡正文，不超过 80 个汉字",
      "visual_strategy": "real_material|img2img|text_on_photo|collage|pure_text|ai_generated",
      "material_ref": "真实材料路径；没有时说明原因"
    }
  ]
}
```

## 完成定义

本地完成必须同时满足：

1. 草稿校验通过。
2. 所有已选择平台的目标文件均已生成。
3. 物化后校验通过。
4. `.codex/state.json` 已记录产物路径与摘要。

发布完成按平台分别记录；任一平台失败不影响其他平台和本地完成状态。

## 编辑契约 v2

新项目 metadata 包含 `editorial_contract_version: 2`、`section_image_policy: content-driven`；复审文件结构见 [editorial-review.md](editorial-review.md)。每次修改后更新受影响的真实复审，不只改文件指纹。

`series-plan.json` 还需 `content_units: [{"id":"u1","source_excerpt":"成稿中的实际短片段"}]`；每个 round 添加 `unit_ids: ["u1"]`、`split_reason`、`standalone_test`、`overlap_review` 字符串。未分配材料需在 unit 添加 `excluded_reason`。不允许各轮复用完全相同材料；少量必要背景重叠由 AI 说明，不能靠改写标题伪装独立。

`draft/visual-plan.md` 记录现有图片审阅、复用/新增/无需图的取舍，以及位置与阅读节奏，正文新增图可为零。`section_images` 只记录实际选用的生成正文图，以独立槽位 ID 为键，包含 `section` 与 `placement_reason`；同节可多张，跨节共用图只登记一次，`section` 写实际插入处。支持各级标题，无标题文章显式填写 `section: ""`。旧标题键仍兼容，但所有项目均取消章节数量和标题后 3 行的图片配额；校验只检查实际登记的图。原图不必转成生成图记录，也不要求 16:9，仍按原意保留。微信预览存在 `draft/preview/`，项目内保留证据，不当作发布正文。


## 平台标题与可选英文版

新项目还必须遵守 [publishing-plan.md](publishing-plan.md)。发布计划单独记录专业博客标题、吸引读者的社交标题、规范分类话题和 AI 英文取舍理由。英文正文与英文图片实际复审后才可分发；editorial-review 的 artifacts 同时绑定 publishing-plan.json 与可选 english.md，内容变化后重新复审。

## 历史文章与微信链接

新项目增加 `related_posts_contract_version: 1`，在 `draft/related-posts.json` 记录实际检索和选取结果，结构见 related-posts.md。微信 HTML 默认把普通外链变为名称、编号和文末完整地址；源 Markdown 保留原链接。确定性呈现经过保真校验，不能因此新增或删减正文。
