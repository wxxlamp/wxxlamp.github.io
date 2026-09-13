# 草稿投递与最终发布

平台状态分别记录：`filled_for_review`（已填充编辑器）、`draft_saved`（草稿已保存）、`submitted`（已提交、审核中）、`published`（已核验对外发布）、`unknown`（超时或中断，结果不明）和 `failed`（明确失败）。审核中不能记成 published；恢复时优先核对 unknown，避免重复发布。

## 能力边界

- 微信公众号可选用外部 `md2wechat` 适配器，经只读检查后写入官方草稿箱。插件不复制其代码，不接触 AppID、Secret 或 API Key。
- 小红书可选用外部 `XiaohongshuSkills` 的 `--preview` 模式填充标题、正文和图片。该模式不会点击发布，也不能证明服务器草稿已经保存，因此只记录 `filled_for_review`。
- 小红书没有在本插件中验证过的公开草稿 API。若当前创作后台显示“保存草稿”，应在已登录浏览器中确认保存成功后，再记录 `draft_saved`。
- CDP 自动化可能触发风控、限流或封号。先用测试账号、控制频率、保留人工复核；验证码、扫码和人机校验必须由用户处理。
- 群发、立即发布和定时发布属于最终外部动作，先展示账号、标题、可见范围和时间；已有覆盖这些具体信息的明确授权即可执行，不因恢复任务重复询问。

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
5. 按账号范围和图片内容指纹隔离缓存，把成功素材的 `media_id` 与 `wechat_url` 缓存在项目 `.codex/wechat-materials.json`，中断后复用，避免重复上传；
6. 只在临时副本中把正文图片替换为微信素材 URL，再调用 `create_draft`，不改写 `article.html`；
7. 创建前先记录 `unknown`，返回非空草稿 `media_id` 后更新为 `wechat/article = draft_saved`，并绑定标题、摘要、作者、HTML、封面及本地图片指纹。相同指纹的重试直接返回已有草稿，内容变化后默认停止，明确需要另建时用 `--new-draft`；未知结果不能用此参数绕过核对。旧版无指纹但已有 media_id 的记录也先核对，不静默再建。

命名账号缓存按别名隔离，默认账号另外绑定适配器配置来源和默认 AppID。若将同一别名重新指向另一个公众号，应先归档旧素材缓存；不要跨账号复用微信 media_id。

### 白名单诊断与重试

`errcode=40164` 的 IP 是微信服务端在失败当次看到的出口，不是对用户配置是否正确的最终判断。先运行：

```bash
python3 <pipeline.py> diagnose-wechat --project <slug>
```

该命令仅读取适配器默认脱敏配置，输出配置来源、默认 AppID 尾号、请求的账号别名、是否配置代理和已有投递结果；不显示 Secret、token 或代理认证信息，也不冒称已经验证出口/接口鉴权。多账号时核对实际别名对应的 AppID，默认 AppID 不能代替命名账号身份。不要用浏览器 IP 检测站代替发布进程的路由。

用户已确认加白后，不再次循环要求其加白：先比对有效账号、环境变量和代理差异，记录请求时间、失败阶段、服务端 IP、脱敏错误及尝试次数。已有明确失败且配置/网络发生变化时只重试一次；同样报错则继续诊断或保留待恢复状态，不连续三次盲试。不凭后续成功断言是缓存或白名单传播延迟。

适配器超时、无有效 JSON、创建响应缺少 media_id 或进程中断，先核对素材库/草稿箱。确定已创建后通过 `record-delivery --status draft_saved --identifier <media_id>` 记录；确认未创建才能记录 failed 后再次投递，说明核对证据。任何输出都必须脱敏。

### 保存后的核对

返回 media_id 证明草稿已保存，不证明清洗后的排版或公开群发成功。优先用可用的只读适配器能力或已登录后台读回，核对中文标题、章节数、图片、封面、重点年份/数字与样式。若已有官方接口 JSON 响应，按 UTF-8 字节解析，避免依赖错误的默认 HTTP 编码把中文误判为乱码；不要额外导出账号密钥来完成核验。当前 md2wechat 不提供草稿读取命令时明确说明核验边界，并保留 media_id 供后台查看。

浏览器被站点安全策略拒绝后，不换浏览器、代理或隐藏接口绕过。可在许可范围内完成已有的草稿适配器工作，受限的后台检查或群发交给用户。

如果未安装适配器，退回已登录浏览器：打开 `wechat/<slug>/article.html`，复制渲染正文，填写标题、摘要、作者和 `metadata.json.wechat_cover_image.local`，确认平台提示保存成功后再记录状态。

## 小红书编辑器与草稿

先复用当前已经打开、已经登录的小红书浏览器和现有标签页，通过 Codex 的浏览器控制能力逐轮安全填充。不要默认启动新的 Chrome，不要创建单独 Profile，也不要因为外部适配器已配置就跳过现有浏览器。

只有当前浏览器无法控制、且用户明确同意使用 CLI 回退时，才在配置 `xiaohongshu_skills_dir` 后执行：

```bash
python3 <pipeline.py> send-draft \
  --project <slug> \
  --channel rednote \
  --round round1 \
  --account <optional-alias> \
  --confirm
```

插件固定调用外部适配器的 `--preview --reuse-existing-tab` 模式，禁止自动追加 `--headless` 或点击发布。`rednote_allow_browser_launch` 默认是 `false`：本地 CDP 端口没有现成浏览器时直接停止，绝不静默新开 Chrome；只有用户明确允许后才能设为 `true`。成功只表示编辑器已经填充，状态记录为 `filled_for_review`。随后需要：

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

无论是否安装 `XiaohongshuSkills`，只要当前已有可控的登录浏览器，就优先使用它完成“填充—复核—保存”流程。页面变化先重读当前页面定位，不能重复调用已关闭的 tab ID。登录、验证码或权限缺失时让用户处理，其间继续不依赖登录的内容工作。用户只要求一篇时只提交选定轮次，其他草稿不能顺手发布。

## 最终发布

最终发布前展示：平台、账号、标题、轮次、可见范围、发布时间和预览结果。沿用本次对话已给出的对应授权，缺少时再确认。提交成功但仍审核中，用 `--status submitted`；仅实际确认对外发布时记录：

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
