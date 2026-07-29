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

该目录包含配置、登录态和个人语气，不得打包进插件或提交到公共仓库。

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
│       ├── round1/post.md
│       ├── round2/post.md
│       └── ...
└── images/
```

`.codex/state.json` 由脚本原子更新，是恢复任务的唯一进度真相。`events.jsonl` 是追加式审计日志。不要把登录 cookie、API token 或浏览器存储复制进项目。

## metadata.json

初始化后补全：

```json
{
  "project": "english-slug",
  "yuque_url": "https://www.yuque.com/...",
  "title": "文章标题",
  "description": "40–60 字描述",
  "tags": ["标签"],
  "categories": ["分类"],
  "cover_image": {
    "url": "https://...",
    "local": "content-projects/.../images/cover.png",
    "ratio": "23:9"
  },
  "section_images": {
    "一级标题": {
      "url": "https://...",
      "local": "...",
      "ratio": "16:9"
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
- front matter 由脚本生成，包含 `title`、`date`、`tags`、`categories`、`description`。
- 正文保持长文完整度和 Hexo Markdown 兼容性。

## 微信公众号

- 目标：`wechat/<slug>/article.md` 与 `article.html`。
- Markdown 不含 Hexo front matter。
- HTML 由 AI 根据文章内容排版，使用行内样式，不加载脚本或外部 CSS；流水线只复制和校验，不得重新排版。
- 实际粘贴后仍需检查代码块、表格、图片宽度和公众号编辑器的二次清洗。

## 小红书

- 目标：`rednote/<slug>/roundN/post.md`。
- 每轮建议 300–900 个可见字符，硬上限由发布时的平台规则决定。
- 每轮必须能够独立理解，包含一个明确标题、一个核心观点或步骤组、配图和 3–8 个相关话题标签。
- 同一事实不在多轮中重复堆砌；系列顺序通过结尾的一句轻量预告连接。

## 完成定义

本地完成必须同时满足：

1. 草稿校验通过。
2. 三个平台目标文件均已生成。
3. 物化后校验通过。
4. `.codex/state.json` 已记录产物路径与摘要。

发布完成按平台分别记录；任一平台失败不影响其他平台和本地完成状态。
