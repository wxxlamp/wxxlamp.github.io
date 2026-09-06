# 平台标题、分类话题与英文版

新项目自动启用 `publishing_contract_version: 1`。所有标题选择、专业价值判断、翻译、图片语言检查由 AI 完成；脚本只核对契约、目录、内容结构与复审指纹。旧项目不强制迁移；需要新能力时在 metadata.json 增加该版本字段，按本文补齐计划，再重新复审，不删除历史成品或投递记录。

## 先做内容判断

1. 沿用已经读取的作者与分类语气档案，并阅读其中提供的少量代表文章，判断当前博客的专业深度；不因出现技术词就生成英文版，也不要再次全站扫描。
2. 执行 `python3 <pipeline.py> publishing-context --project <slug>`，读取当前分类话题目录、`catalog_sha256`、`source_sha256`。稿件增删图片或正文后重新执行。
3. AI 写入 `draft/publishing-plan.json`。正文首图与章节图生成前先确定英文取舍，准备双语 brief；最终插图完成后更新计划指纹。

## 标题策略

- 博客：对象明确、范围准确、专业清晰；优先“技术对象：问题与方法”“系统名称：设计与实践”。修复记录交代故障与原因；读书、年度回顾和个人经历保留作者语气，不硬改成技术论文。不使用夸大承诺、营销词、悬念堆叠和感叹号。
- 公众号：先提出 2–3 个候选，再选最能体现读者问题、具体收益或有依据的反常识判断的标题。允许提问、具体数字与故事切口，禁止虚构收益、经历和数据。最多 64 字，不把营销标题复制回博客。
- 小红书：每篇独立选标题，贴近读者场景，先交代对象，再表达真实的冲突或收益；符合现有平台长度限制。`titles.rednote.roundN.text` 必须与对应 `post.md` 的一级标题完全一致；卡片封面可缩为 12 字以内，不能增加正文未支持的承诺。
- `--title` / metadata.title 是原始素材标题。实际博客与微信发布分别使用计划中的标题；小红书使用每轮稿件标题。

## 分类与话题

目录默认位于工作区 `source/_data/taxonomy.json`，可用配置 `taxonomy_catalog` 改路径。每个目录条目包含 `zh` 与 `en`，话题另含稳定 `id`。没有目录时，从当前中文文章 front matter 读取已有名称供 AI 选择。

- 每篇恰好一个分类、1–3 个核心话题。分类表达长期内容领域，话题表达正文重点讨论的技术、问题或经历。
- 按主要论证归属，不把顺带提及的 Java、AI、数据库全打上标签。不把文章标题、年份、泛泛的“技术”或英文同义词另建话题。
- 本博客区块链属于“基础夯实”，话题可选“区块链”；面试记录属于求职内容，不能因含技术词就作为专业英文教程。
- 中文和英文稿 front matter 使用相同的规范中文名称；前端通过目录映射英文显示。新增概念先检查现有目录能否覆盖，确需新增时同时补 `zh`、`en` 和稳定 id，再重新获取指纹。

## 何时生成英文版

默认优先考虑可复用的工程实践、系统设计、完整故障分析、有实质论证的 AI/智能体文章、对国际读者有用的跨境业务知识。AI 必须具体说明目标读者和翻译收益。

面试题库、面经、零散备忘、本地生活攻略和缺乏普遍意义的个人流水账通常跳过。年度回顾、求学或管理经历可以在有可迁移的经验且适合国际读者时选入，不机械按分类决定。不补编专业深度，也不为了英文篇数翻译所有文章。

选择生成后，完整翻译成 `draft/english.md`，不带 front matter，不用摘要替代全文。保留论证、限制条件、事实、链接、代码与公式；可自然调整语言，但不删章节或例子。英文标题同样专业清晰。AI 需逐节复核中英文对应，并将 english 的语气、自然度、错字、格式与事实审阅写入 editorial-review.json。

### 英文图片

- 覆盖英文正文中的每张图，包括语雀原图、HTML 图片、首图和后续章节配图。
- 有中文文字的图必须生成对应英文图：标题、坐标、图例、注释、界面说明与图内标签都应为英文；准确保留技术关系和数值，不能只翻译 alt 文本。使用本地截图作参考前先实际查看。
- 无文字的照片、插画可以复用，但必须实际查看并记录 `language: no-text` 和检查理由。无法准确重绘且没有可读英文替代时，先解决图片问题；不能把不完整英文稿标记可发布。
- 英文图上传：`python3 <pipeline.py> upload-image --project <slug> --kind <cover|section> --key <key> --file <path> --language en`。它记录到 metadata.english_images，不覆盖中文图片。
- 在计划中逐张映射源 URL 与英文 URL，记录语言、检查状态和具体检查结论。改变图片、正文、标题或分类后，重新生成对应 SHA-256 并复审。

## 契约示例

```json
{
  "version": 1,
  "source_sha256": "<publishing-context 输出>",
  "titles": {
    "blog": {"text": "消息消费幂等：重复投递的处理策略", "reason": "说明问题对象与文章范围"},
    "wechat": {"text": "消息重复消费，为什么重试反而越修越乱？", "reason": "正文解释重试与幂等边界，用实际问题吸引读者"},
    "rednote": {
      "round1": {"text": "消息重复消费，我先检查这三个地方", "reason": "正文确有三个可操作检查项"}
    }
  },
  "taxonomy": {
    "catalog_sha256": "<publishing-context 输出>",
    "categories": ["基础夯实"],
    "topics": ["消息队列", "分布式系统"],
    "reason": "核心讨论分布式消息的重复投递与幂等"
  },
  "english": {
    "decision": "generate",
    "reason": "幂等策略具有跨平台的工程复用价值，文章提供完整机制与限制",
    "audience": "Backend engineers implementing message consumers",
    "title": "Idempotent Message Consumption: Handling Duplicate Deliveries",
    "description": "Practical strategies and limitations for handling duplicate message deliveries.",
    "images": [
      {
        "source_url": "https://example.com/diagram-zh.png",
        "url": "https://example.com/diagram-en.png",
        "language": "en",
        "review_status": "passed",
        "review_note": "逐一核对英文节点、重试箭头与幂等键标注，与中文机制一致"
      }
    ]
  }
}
```

仅填写已选平台的标题。若跳过英文，使用 `"english": {"decision": "skip", "reason": "<与具体内容有关的理由>"}`；不要遗留 english.md。只选社交平台时无需 taxonomy / english 字段。示例标题、理由和图片均为格式说明，必须针对真实文章重新判断。

复审 artifacts 必须含 `draft/publishing-plan.json`；生成英文时还需 `draft/english.md`。使用 SHA-256 对文件原始字节求值，不能自己编造指纹。`materialize` 写出 `source/_posts/<slug>.md` 与可选 `source/_posts/en/<slug>.md`；英文 front matter 使用 `lang: en`、`translation_of: <slug>`，并与中文共享日期、分类和话题。旧英文稿存在且当前决策为跳过时会停止，要求明确处理，避免静默删除或误发布。


## 引用语言与来源（reference contract v1）

新项目自动记录 `metadata.reference_contract_version: 1`。`publishing-context` 同时返回 `references`，包含真实存在的站内双语路由、已核验的外部同源中英文对照和 `sha256`。把该值写入发布计划 `references_sha256`，分别填写 `references_review.zh` / `references_review.en` 的实际检查说明（不生成英文时只需 zh）。复审仍绑定整个计划与成稿，引用改动后重新审阅。

1. 中文稿引用中文页面，英文稿引用英文页面。站内链接根据文章日期、slug、lang 和 translation_of 匹配真实存在的译文；保留查询参数、章节锚点。兼容绝对 URL、相对站点路径、旧域名、Markdown 引用式链接、HTML 链接和裸 URL，代码及图片地址不当作文章引用改写。
2. 不得机械添加 `/en/`，也不能把整篇文章链接当作某个不同内容的来源。目标不存在就修复旧地址或补译被引用文章；尚不补译时，保留原始出处并明确标注 `in Chinese` / `英文原文`，说明原因。用户要求引用全部同语言时，补齐站内被引用文章后再完成。
3. 外部资料优先选择同一官方文档的对应语言版本，实际打开确认内容和锚点。不存在同语言版本的论文、原始采访、博客文章和课程，不用不相关的英语资料冒充翻译；保留原始出处并标明语言。代码仓库、产品入口和其他语言中立的资源可共用。
4. 工作区 `source/_data/references.json`（配置键 `reference_catalog`）可记录 `site_aliases`、`route_aliases`、`pairs: [{"zh": "...", "en": "..."}]` 与 `original_sources: [{"url": "...", "language": "zh"}]`。只登记已经检查过的对应关系，不根据网址模式猜测。
5. 新的外部同源译文尚未收录目录时，在计划 `reference_links` 中填写 `source_url`、英文 `url`、`review_status: passed` 和具体 `review_note`。脚本接受经过记录的对应译文，不再要求中英稿引用 URL 完全一样；已知站内路由不能被手工映射覆盖。脚本只能验证结构与审阅记录，远程语言和内容等价性必须由 AI 实际检查。
6. 跨段或全文的同语言对应关系不能只检查“Read in English”按钮，还要逐一检查正文、引用块、参考资料和裸链接。本站英文标题锚点复用中文文章锚点，保留片段并在生成页面中确认存在。自引用优先使用 `#section`。

计划补充示例：

```json
{
  "references_sha256": "<publishing-context.references.sha256>",
  "references_review": {
    "zh": "正文中的站内引用均指向中文原稿；官方文档切换为已核对的中文版。",
    "en": "站内引用均有对应英文文件；外部文档核对了主题、版本与章节锚点。"
  },
  "reference_links": [
    {
      "source_url": "https://docs.example/zh/topic",
      "url": "https://docs.example/en/topic",
      "review_status": "passed",
      "review_note": "实际阅读同一官方文档的两个语言版本，论据与所引章节一致。"
    }
  ]
}
```

旧项目不自动修改正文或状态；需要启用此项时添加 metadata.reference_contract_version: 1，重新获取目录指纹并补齐复审。新增被引用译文后重新执行 publishing-context，避免沿用“只有中文”的旧判断。
