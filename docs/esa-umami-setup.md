# 阿里云 ESA 与 Umami Cloud 接入

## 当前状态（2026-09-08）

- 用户选择 ESA 免费版和 Umami Cloud 免费版，保留 jsDelivr 图片。
- ESA 控制台已登录。在添加 `wxxlamp.cn` 的区域选择步骤，控制台显示“您的域名未备案”，中国内地和全球区域均禁用。用户随后确认备案未成功。
- 尚未创建 ESA 站点、购买套餐或切换 DNS；线上仍由 GitHub Pages 提供服务。
- Umami Cloud 已创建网站“王星星的魔灯”（`wxxlamp.cn`），主题已配置真实 website ID `27d58970-f2c7-47fb-a0ea-380f8123c229` 和官方脚本地址。
- 后台地址：https://cloud.umami.is/analytics/us/websites/27d58970-f2c7-47fb-a0ea-380f8123c229 。需要登录，不公开分享。
- 用户暂缓处理备案，ESA 保持未接入。Umami 待用户发布代码后才能验证线上接收与手机刷新去重。
- 本地配置已关闭不蒜子，不再展示其不可靠的历史总数。此更改尚未发布。

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

## 发布

遵守仓库约定：提交前展示暂存差异并获得确认，不自动推送。真实 website ID 已配置，本地测试、构建和预览检查通过；由用户手动推送 `deploy` 分支触发现有 GitHub Actions 发布。

参考：[ESA 接入](https://help.aliyun.com/zh/edge-security-acceleration/esa/getting-started/add-your-website-to-esa)、[Umami 配置](https://docs.umami.is/docs/tracker-configuration)。
