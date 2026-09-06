# 编辑复审 v2：具体证据与当前文件绑定

新建项目自动使用 `metadata.editorial_contract_version: 2` 与 `section_image_policy: content-driven`。旧项目恢复时保留已有文件，继续加工前设置这两项并补齐本复审；旧版状态兼容读取，校验会提示迁移，不把旧的 passed 自动继承成新标准。metadata 可以编辑，`.codex/state.json` 仍只由流水线管理。

## 审阅范围

两种 edit_mode 都检查语气、错字、标点格式和知识错误。`correction-only` 只做确定性的局部修正；知识有疑点时记录问题与依据，不擅自扩写论证。可核实的知识错误以最小改动订正，涉及作者核心立场、私有经历且材料不足时保持待确认，继续其他可完成的工作。

先做内容遍，再做声音遍，最后逐个读平台成品，包括小红书卡片。写具体观察或改动，不只写“检查通过”。

- 语气：人称、直接程度、情绪和技术密度是否符合这类历史文章？保留原稿真实细节，不能从历史文章借经历填进新稿。
- 自然表达：开头是否进入具体事，句段是否同节奏，结尾是否强行升华，标题是否夸张，互动是否像群发模板？不要机械删除“其实”“所以”等作者常用承接词，也不要为了不整齐刻意制造口误。
- 错字与格式：同音词、重复字、的地得、术语、版本号、数字单位、中英文标点、标题层级、代码围栏、引用链接、表格列与图片说明。编号要求只针对博客和微信章节，代码中的 # 与小红书发布标题不套用章节编号。
- 知识：逐项找数字、版本/API、因果、绝对结论、引文、时效规则与代码行为。历史博客只能证明作者语气，不能证明知识正确。价格/政策/产品现状等必须检索当前权威来源，技术查官方文档、源码或论文；引用注明具体来源和日期。必要时做最小可复现实验；没有执行就不能写“已验证”。
- 无法核实：限定为作者经验或明确假设、删去不影响论证的可疑断言，或保持待确认。不能拿一个搜索摘要或弱来源盖章 passed，也不能通过加“可能”掩盖支撑主论点的缺失证据。

## 记录结构

在 `draft/editorial-review.json` 写入以下结构。所有指纹是相应文件当前字节的 SHA-256；`artifacts` 覆盖 raw/source.md、draft/polished.md、已选渠道的 Markdown/HTML、series-plan.json 及每轮 cards.json。只有 AI 完成实际审阅后填写 passed；脚本只核验记录完整、材料引用可定位和版本一致，不证明文字自然或事实真实。

```json
{
  "status": "passed",
  "voice_sha256": "当前工作区 author-voice.md 的 SHA-256",
  "artifacts": {"raw/source.md": "文件 SHA-256", "draft/polished.md": "文件 SHA-256"},
  "reviews": {
    "polished": {
      "voice": "具体保留的作者表达特征及其理由",
      "naturalness": "具体删改的模板话；没有问题则说明观察依据",
      "typos": "错字、标点及术语检查结果",
      "format": "编号、引用、代码与表格检查结果",
      "facts": "核查了哪些主张，与下方证据对应"
    }
  },
  "fact_scope": "核查范围、采用版本，以及未独立验证的作者经历",
  "fact_checks": [
    {
      "claim": "被核查的具体主张",
      "location": "文件与段落/卡片位置",
      "status": "corrected",
      "basis": "原说法、订正结果及证据如何支持",
      "time_sensitive": true,
      "source_url": "https://权威来源的实际页面",
      "checked_at": "实际核查日期"
    }
  ]
}
```

`reviews` 还需所选平台的 `wechat`、`round1`、`round2` 等条目，均包含相同五项。每轮 review 同时覆盖 post 与 cards；不要把博客 review 复制成全平台通过。

事实状态允许 `verified`、`corrected`、`qualified`、`removed`、`author-account`。无外部知识可用空 `fact_checks`，但必须解释 fact_scope。私有经历标 author-account，不能声称已外部查证。没有历史样本时省略 voice_sha256，改写 `voice_mode: cold-start` 和 `voice_limitation`；有历史样本不允许用冷启动绕过档案。

微信额外添加：

```json
{
  "wechat_layout": {
    "status": "passed",
    "notes": "实际观察结果、修正内容与尚未验证的平台粘贴效果",
    "previews": [
      {"width":375,"path":"draft/preview/wechat-375.png","sha256":"截图 SHA-256","html_sha256":"当前 HTML SHA-256"},
      {"width":430,"path":"draft/preview/wechat-430.png","sha256":"截图 SHA-256","html_sha256":"当前 HTML SHA-256"}
    ]
  }
}
```

从预览脚本生成的 layout-evidence.json 复制 previews，然后实际查看图片再填 status 与 notes。润色、换图、改卡片后文件指纹变化会使复审失效；更新相关观察再计算新指纹，不能仅重新填哈希。


## 平台标题与可选英文版

新项目还必须遵守 [publishing-plan.md](publishing-plan.md)。发布计划单独记录专业博客标题、吸引读者的社交标题、规范分类话题和 AI 英文取舍理由。英文正文与英文图片实际复审后才可分发；editorial-review 的 artifacts 同时绑定 publishing-plan.json 与可选 english.md，内容变化后重新复审。
