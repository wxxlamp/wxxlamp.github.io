# 简历访问统计

主题配置 `umami.resume.enable: true` 为中英文简历启用自建 Umami 手动统计；同时需要 `umami.enable` 和 `website_id`。简历不加载 Google Analytics、百度、Clarity 或 Umami Cloud。其他私密页继续排除。

在自建 Umami 后台选择本站和日期范围，按以下 URL 筛选，查看 Views（PV）及 Visitors（UV）：

| URL | 含义 |
| --- | --- |
| `/resume-stats/entry` | 每次打开简历页，含免密回访 |
| `/resume-stats/locked` | 实际显示密码输入框 |
| `/resume-stats/content` | 正文显示成功，含密码验证与缓存授权 |

这些是统计用的虚拟路径，没有对应网页。每个阶段每次页面加载最多记录一次；刷新或中英文切换是新的页面访问。错误密码不记录正文访问。免密回访仅记录入口和正文。后台应按完整 URL 筛选，避免混合各阶段。

Tag 用于进一步筛选：`resume:zh` / `resume:en` 表示入口或密码页语言；正文使用 `resume:zh:password`、`resume:zh:cached`、`resume:en:password`、`resume:en:cached`，分别表示语言与本次授权方式。中英文使用同一阶段路径，UV 由 Umami 去重，不手动相加。UV 采用 Umami 的匿名访客口径，不等同于跨设备永久去重的自然人数。

只发送阶段、固定标题、标签和 Umami 基础访客属性，不发送密码、正文、原页面标题、查询参数或来源 URL。统计脚本异步加载前的阶段会暂存，加载后按顺序发送；脚本被拦截或请求失败会导致漏计，但不阻塞查看简历，也不重试以免重复计数。限制正式域名，本地预览不收数。

## 博客全站数字

三个阶段属于同一站点的页面浏览，因此会进入 Umami 未筛选的总 PV。分析普通博客访问时，应排除 URL 前缀 `/resume-stats/`。页脚公开数字由独立 Umami 仓库中的 `/api/public/blog-stats` 提供，本仓库无法替它增加服务器端过滤；如需该数字只包含普通博客访问，需要在该接口中同样排除这些路径（PV 和 UV 都应过滤后计算）。

## 发布验证

本地测试验证埋点行为；正式收数需要发布后检查：

1. 无当月授权的浏览器打开简历，后台出现 entry、locked。
2. 输入错误密码，不增加 content；输入正确密码，增加一次 content，Tag 为 password。
3. 刷新后出现 entry、content，Tag 为 cached，不增加 locked。
4. 切换英文版，确认路径相同、Tag 变为 en。
5. 查看各阶段 Visitors；不要将阶段 UV 或语言 UV 相加。历史数据无法补录。

参考：[Umami Tracker functions](https://docs.umami.is/docs/tracker-functions)、[Tracker configuration](https://docs.umami.is/docs/tracker-configuration)。
