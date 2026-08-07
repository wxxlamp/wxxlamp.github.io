# 草稿投递与最终发布

平台能力分为三个明确状态：`filled_for_review`（已填充编辑器）、`draft_saved`（平台草稿已保存）和 `published`（已对外发布）。不得把前一个状态写成后一个状态。

## 能力边界

- 微信公众号可选用外部 `md2wechat` 适配器，经只读检查后写入官方草稿箱。插件不复制其代码，不接触 AppID、Secret 或 API Key。
- 小红书可选用外部 `XiaohongshuSkills` 的 `--preview` 模式填充标题、正文和图片。该模式不会点击发布，也不能证明服务器草稿已经保存，因此只记录 `filled_for_review`。
- 小红书没有在本插件中验证过的公开草稿 API。若当前创作后台显示“保存草稿”，应在已登录浏览器中确认保存成功后，再记录 `draft_saved`。
- CDP 自动化可能触发风控、限流或封号。先用测试账号、控制频率、保留人工复核；验证码、扫码和人机校验必须由用户处理。
- 群发、立即发布和定时发布属于最终外部动作，必须展示账号、标题、可见范围和时间，并取得用户明确确认。

## 发布前事实检查

每次先运行：

```bash
python3 <pipeline.py> resume --project <slug>
python3 <pipeline.py> validate --project <slug> --phase materialized
python3 <pipeline.py> inspect --project <slug> --probe
```

`inspect` 的 `targets.*.blockers` 是当前项目的发布就绪事实来源。它同时报告文章字符数、标题层级、远程图片数、描述长度、AI 套话风险、适配器路径和投递能力。实际是否已经保存，以 `deliveries` 为准；不能把“适配器可用”写成 `draft_saved`。

## 个人博客

1. 检查 Hexo front matter、正文 diff、链接和图片。
2. 运行仓库规定的构建或预览命令。
3. 只有用户明确要求且仓库规则允许时才暂存、提交或推送。本仓库禁止 Codex push，应交给用户手工执行。
4. 博客 Git 状态与平台草稿状态独立，不使用统一的 `drafted` 阶段覆盖彼此。

## 微信公众号草稿箱

在工作区配置 `md2wechat_executable`，多账号时可配置 `wechat_account`。先让适配器自身完成 AppID、Secret、账号权限和 IP 白名单设置。Chrome 登录态不能替代官方 API 的 IP 白名单。

插件已经生成并复审 `article.html`，因此默认直接复用这份 HTML，不再调用转换 API。`MD2WECHAT_API_KEY` 缺失但 `doctor.data.readiness.draft` 为 `true` 时仍可投递；只有草稿凭据不可用才阻断。

写入草稿箱：

```bash
python3 <pipeline.py> send-draft \
  --project <slug> \
  --channel wechat \
  --account <optional-alias> \
  --confirm
```

命令会：

1. 再次校验 materialized 产物和本地 2.35:1 封面；
2. 创建带标题、摘要 front matter 的临时 Markdown，不修改最终文章；
3. 先执行 `md2wechat inspect ... --draft --cover ... --json`；
4. 按 `metadata.json` 将 HTML 中的公开图片 URL 映射回既有本地图片，并通过 `upload_image` 上传封面与正文图片；无法映射的远程图片使用 `download_and_upload`；
5. 把成功素材的 `media_id` 与 `wechat_url` 缓存在项目 `.codex/wechat-materials.json`，中断后复用，避免重复上传；
6. 只在临时副本中把正文图片替换为微信素材 URL，再调用 `create_draft`，不改写 `article.html`；
7. 仅在返回非空草稿 `media_id` 后记录 `wechat/article = draft_saved`。

如果适配器报 `errcode=40164`，展示脱敏后的出口 IP，要求用户将其加入公众号 IP 白名单。适配器超时时不要自动重试：平台侧结果可能已经成功，应先检查素材库或草稿箱，避免重复项。任何错误输出都必须遮蔽 Secret 与 access token。

如果未安装适配器，退回已登录浏览器：打开 `wechat/<slug>/article.html`，复制渲染正文，填写标题、摘要、作者和 `metadata.json.wechat_cover_image.local`，确认平台提示保存成功后再记录状态。

## 小红书编辑器与草稿

配置 `xiaohongshu_skills_dir` 后，逐轮安全填充：

```bash
python3 <pipeline.py> send-draft \
  --project <slug> \
  --channel rednote \
  --round round1 \
  --account <optional-alias> \
  --confirm
```

插件固定调用外部适配器的 `--preview` 模式，禁止自动追加 `--headless` 或点击发布。成功只表示编辑器已经填充，状态记录为 `filled_for_review`。随后需要：

1. 核对标题、正文、话题和全部本地上传图片；
2. 确认当前账号与轮次；
3. 若页面存在草稿保存能力，执行保存并等待成功提示；
4. 再记录服务器草稿状态：

```bash
python3 <pipeline.py> record-delivery \
  --project <slug> \
  --channel rednote \
  --round round1 \
  --status draft_saved \
  --account <alias> \
  --identifier <visible-draft-id> \
  --note "平台已显示保存成功"
```

没有 `XiaohongshuSkills` 时，使用当前可用的已登录浏览器控制能力完成同样的“填充—复核—保存”流程。平台改版、文件上传权限不足或选择器失效时暂停并让用户接管。

## 最终发布

最终发布前展示：平台、账号、标题、轮次、可见范围、发布时间和预览结果。用户明确确认后才能执行，并逐平台记录：

```bash
python3 <pipeline.py> record-delivery \
  --project <slug> \
  --channel <wechat|rednote> \
  --round <optional-roundN> \
  --status published \
  --account <alias> \
  --identifier <platform-id>
```

状态文件只记录账号别名、标题或平台标识、结果和失败原因；绝不记录 Cookie、token、验证码、AppSecret 或完整登录凭据。
