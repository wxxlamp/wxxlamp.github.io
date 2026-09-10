# 阿里云 ESA 与 Umami 接入

## 自建 Umami 与三路采集（2026-09-10，待发布）

- 自建 Umami 3.3.1 已部署：<https://wxxlamp-umami.vercel.app>；仓库为 <https://github.com/wxxlamp/umami>。
- Vercel 项目 `Light Tech / wxxlamp-umami` 使用 Hobby 套餐；Neon 同名项目使用 Free 套餐、Postgres 18、新加坡区域。Vercel 的 `sin1` 配置尚待提交发布。
- 自建站点 ID：`7ae63952-76fc-4a90-a5b7-aedd93fb56c9`；Cloud 站点 ID：`27d58970-f2c7-47fb-a0ea-380f8123c229`。
- 用户最新选择：自建 Umami、Umami Cloud、不蒜子持续独立采集；前台只展示自建 Umami 的累计全站和本文 PV/UV，不回退到不蒜子、不相加。有效的 0 正常展示；错误、无效响应或 10 秒超时显示“统计暂不可用”。
- 两份 Umami 脚本异步独立加载；限定正式域名，排除私密页面、查询参数和锚点。不蒜子计数节点隐藏，避免其响应改写展示数字。
- 自建仓库新增 `/api/public/blog-stats`：固定本站 ID，无管理员凭据，仅返回全站及可选文章路径的汇总 PV/UV；服务器与 CDN 缓存各 60 秒，因此数字不会保证刷新后立即增加。不能查询其他站点、日期范围或访客明细。
- UV 使用 Umami 的匿名 session 去重口径，不等同于跨设备、跨网络、跨所有日期永久去重的自然人数。自建历史从接入日起累计，不迁移或合并 Cloud、不蒜子的历史值。
- 管理员初始密码已更换且登录验证通过；用户最新指定的密码尚待用户在个人资料页手动修改。密码、数据库连接、API token 不进入源码和前端。
- 部署时已用临时站点验证真实采集：PV 1→2，UV 保持 1；测试站点已删除。新公开接口及三路采集配置仍待提交发布，线上目前保留之前版本。
- 未接入统计自定义域名；默认 `vercel.app` 的大陆可达性尚未实测。未变更 DNS、购买付费套餐或实现个人密码服务。

### 发布顺序

1. 先提交自建 Umami 的公开接口、测试和新加坡区域配置，等待 Vercel 构建成功。
2. 检查公开接口成功响应、非文章路径返回 400、接口仅含汇总数字。
3. 再提交博客主题、脚本和测试，在 GitHub Actions 发布完成后验证双 Umami 收数及前台汇总显示。
4. 不蒜子持续采集但不展示。需要回滚时回退对应博客提交，恢复先前展示逻辑；不用改写历史计数。

## 早期接入记录（2026-09-08）

- 用户选择 ESA 免费版和 Umami Cloud 免费版，保留 jsDelivr 图片。
- ESA 控制台已登录。在添加 `wxxlamp.cn` 的区域选择步骤，控制台显示“您的域名未备案”，中国内地和全球区域均禁用。用户随后确认备案未成功。
- 尚未创建 ESA 站点、购买套餐或切换 DNS；线上仍由 GitHub Pages 提供服务。
- Umami Cloud 已创建网站“王星星的魔灯”（`wxxlamp.cn`），主题已配置真实 website ID `27d58970-f2c7-47fb-a0ea-380f8123c229` 和官方脚本地址。
- 后台地址：https://cloud.umami.is/analytics/us/websites/27d58970-f2c7-47fb-a0ea-380f8123c229 。需要登录，不公开分享。
- 用户暂缓处理备案，ESA 保持未接入。Umami 待用户发布代码后才能验证线上接收与手机刷新去重。
- 2026-09-09：用户确认需要公开数字，接入 `busuanzi.cc` 显示全站与本文 PV/UV，Umami 保留独立后台。两个来源不混用；此项已发布。

## ESA 配置目标

1. 先确认备案识别正常，再选择包含中国内地的区域、免费套餐。
2. 优先 CNAME 接入，保留现有 DNS；源站使用 GitHub Pages 地址，核对回源 Host、HTTPS SNI 和证书，避免用已指向 ESA 的域名作为源站形成循环。
3. 缓存成功响应的文章 HTML（建议边缘 TTL 10 分钟）；站内 CSS/JS、图片可用较长边缘 TTL。没有内容哈希的文件不要设置浏览器永久缓存。
4. 错误页、重定向及统计上报接口不套用 HTML 长缓存。
5. 先验证首页、中英文文章、CSS/JS、图片、404 和 HTTPS，再切换正式解析。记录切换前 DNS 值以便回退。
6. 发布文章后刷新对应 HTML 缓存；修改公共样式后刷新对应资源。jsDelivr 外链仍走原 CDN。

## Umami 配置目标

1. 登录免费账号，在后台添加网站 `wxxlamp.cn`。
2. 将后台 tracking code 的公开 website ID 和 script URL 填入 `themes/wxx-theme/_config.yml` 的 `umami`。不在仓库或前端放 API 密钥。
3. 仅统计 `wxxlamp.cn`，排除本地预览和私密页面。忽略查询参数及目录锚点，避免同一文章的数据拆分。
4. 在后台按页面 URL 和日期范围查看 Views（PV）、Visitors（UV）；这里不自动向公众开放统计后台，也不在文章中暴露账户 API。
5. 发布后用同一手机、同一网络连续刷新，核实 PV 增加且 UV 稳定；再检查电脑与手机访问均到达后台。换设备或网络可能影响 Umami 的访客识别。
6. 新统计从正式接入时开始，不将不蒜子历史值当成 Umami 的历史数据。

## 后续发布

自建 Umami 跟踪配置发布后，在正式博客访问文章并检查自建后台收数；手机刷新去重需要在实际手机和网络环境下验证。若跟踪服务不可达，可将主题 `umami` 配置回退到上方历史记录中的 Cloud 配置；不蒜子公开计数独立运行。凭据轮换在 Umami、Vercel、Neon 控制台完成，切勿提交密码、连接串或管理员 API token。

参考：[ESA 接入](https://help.aliyun.com/zh/edge-security-acceleration/esa/getting-started/add-your-website-to-esa)、[Umami 配置](https://docs.umami.is/docs/tracker-configuration)。
