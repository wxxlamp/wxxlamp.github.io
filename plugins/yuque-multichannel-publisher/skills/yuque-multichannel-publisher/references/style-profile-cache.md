# AI 语气档案缓存

## 原则

语气判断始终由 AI 完成。先读取工作区 `style-profiles/author-voice.md`；缺少时按 `voice-profile.md` 首次学习并写入工作区。`style_profiles.py` 只负责可选的分类差异：枚举分类文章、计算内容指纹、选择刷新范围、校验档案结构和持久化，不统计句长、不提取高频词、不改写正文。

缓存放在工作区 `.codex/yuque-multichannel-publisher/style-profiles/`，不会随插件复制给其他人。每个分类对应一个不超过 16 KB 的 JSON，只保留抽象写作特征，不保存文章全文。

## 每次润色前

```bash
python3 plugins/yuque-multichannel-publisher/skills/yuque-multichannel-publisher/scripts/style_profiles.py \
  prepare --category "<分类>"
```

按输出的 `action` 执行：

- `reuse`：只读取 `profile_path`。禁止重新读取样本。
- `learn`：首次建立档案。读取 `read_samples` 中的 3–8 篇文章。
- `refresh`：先读取旧 `profile_path`，再读取 `read_samples` 中的变化文章和锚点文章；不要重读整个分类。
- `blocked`：该分类没有样本。改用 `default` 档案；仍不存在时使用自然、克制的默认语气，并明确这是冷启动。

`default` 是跨分类兜底档案，只有在缺少精确分类档案时使用。不得用它覆盖已经存在的分类档案。

## AI 生成档案

将 AI 提炼结果写入临时 JSON。必填字段：

```json
{
  "voice": "整体语气与可信度特征",
  "narrative_perspective": "人称、作者与读者关系",
  "sentence_style": "句长、节奏和句式",
  "paragraph_style": "段落长度与单段职责",
  "technical_detail": "技术细节、例子和边界条件密度",
  "opening": "常见开场方式",
  "ending": "常见收束方式",
  "structure": ["文章组织习惯"],
  "transitions": ["常用转场策略"],
  "preferred_expressions": ["偏好的表达特征"],
  "avoid_expressions": ["需要避免的词语和 AI 腔"],
  "fact_boundaries": ["不得虚构或越界的内容"],
  "micro_examples": ["可选，最多 5 条，每条不超过 120 字"]
}
```

`micro_examples` 应当是 AI 自己概括或新写的微型示例，不能长段复制样本。禁止加入 `articles`、`full_text`、`source_content`、`raw_samples` 等全文字段。

## 保存

```bash
python3 plugins/yuque-multichannel-publisher/skills/yuque-multichannel-publisher/scripts/style_profiles.py \
  save \
  --category "<分类>" \
  --input <AI生成的profile.json> \
  --samples <sample1.md> <sample2.md> <sample3.md>
```

脚本会把分类和紧凑风格特征写进工作区 profile；完整分类语料指纹、样本路径和哈希写进同一工作区的脚本专用 `profile-index.json`。AI 在缓存命中时只读取 profile，不读取较大的索引。后续 `prepare` 使用索引判断缓存是否仍然有效。

## 刷新策略

- 分类语料指纹不变：直接复用。
- 新增、修改或删除文章：增量刷新。
- 用户明确要求重新学习：重新读取 3–8 篇代表作并覆盖档案。
- 写作风格有意转型：建立新分类档案，不在旧档案中混入互相矛盾的风格。

不要把其他工具生成的全文缓存整体加载到上下文；它们不能达到节省 token 的目标。
