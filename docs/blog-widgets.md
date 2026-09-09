# 代码高亮、访问统计与评论

## 代码高亮

中英文文章均通过 `hexo.post.render()` 的文章处理流程进行构建期高亮。
代码围栏应声明语言，例如 `java`、`python`、`sql`、`json`、`bash`。
现有文章中的 `shell` 表示无提示符的 Shell 命令，按 Bash 语法处理；
无语言、`text` 或未知语言保留纯文本，避免猜错代码类型。

修改 SCSS 局部文件或渲染脚本后，执行 `npm run clean && npm run build`，
避免 Hexo 缓存保留旧的代码块或样式。

## 访问统计

2026-09-09 按用户要求恢复公开数字：采用 `busuanzi.cc` 3.6.9，页脚显示
全站 PV/UV，文章标题下显示本文 PV/UV；Umami Cloud 继续用于独立后台分析。
两个服务口径不同，数字不要求一致，不迁移或叠加旧服务历史基数。
原推荐的 soxft 公共实例 `busuanzi.9420.ltd` 在接入检查时证书过期，未采用。

新服务脚本为 `https://cdn.busuanzi.cc/busuanzi/3.6.9/busuanzi.min.js`。
HTTPS 和跨域请求已验证，同一网络连续两次不携带 Cookie 的测试返回
全站/本文 `(PV, UV) = (1, 1)、(2, 1)`，这两次测试已计入新服务。
服务文档描述 UV 按 IP 去重：共享出口可能合并访客，切换网络可能新增 UV，
不能视为精确自然人数。真实手机浏览器验证仍需发布后进行。

私密页面不加载计数器；本地和备用域名不发计数请求。仅成功获得有效数字时
显示计数，失败显示“统计暂不可用”。全站与文章结果分别处理，脚本每页仅加载一次。
参考：[busuanzi.cc 使用说明](https://www.busuanzi.cc/doc.php)。

接入状态及后台入口见 [ESA 与 Umami 接入记录](esa-umami-setup.md)。
以下为旧版 `busuanzi.ibruce.info` 的排查记录，当前不再使用该接口。

旧版页脚显示其**全站累计** PV 和 UV，不是当前文章或当天的数据。
仅 `_config.yml` 中 `url` 的正式 origin 发出请求，本地预览、IP 和备用域名
不计数，也不显示其他域名的共享统计。每个页面只加载一次统计脚本。
网络失败、超时或无效结果显示“统计暂不可用”，不以 0 或缓存数据替代。

不蒜子历史数据仍由原服务保存，不导入 Umami，也没有人为修改基数。
去重和历史累计由不蒜子服务器负责；前端不能修复服务端的历史误计数，
也不能保证 UV 等于真实自然人数或 GA4 的用户数。
2026-09-07 排查时接口曾返回 HTTP 502，之后浏览器恢复获得统计值。

同日针对手机刷新 UV 增加进行了 Cookie 对照检查：服务返回
`busuanziId` Cookie，属性为 `HttpOnly; Secure; SameSite=None`，
所属域名为 `busuanzi.ibruce.info`。相对博客它属于第三方 Cookie。
保留 Cookie 的连续请求得到 `(PV, UV) = (6748, 5374)、(6749, 5374)`；
随后不携带 Cookie 的请求得到 `(6750, 5375)`，复现了缺失标识时 UV 增加。
这符合手机浏览器阻止或不保留第三方 Cookie 的表现，具体手机环境尚未检查。
Safari 的相关行为见 [WebKit 官方说明](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/)。
预览隔离和异常提示无法修复此服务端去重限制；可靠的替代方案需要使用本站
第一方访客标识和服务端去重，不能通过少发 PV 请求或固定显示 UV 来掩盖误计数。

参考：[不蒜子原作者说明](https://ibruce.info/2015/04/04/busuanzi/)。

## 评论启用

2026-09-07 已通过仓库设置开启 `wxxlamp/wxxlamp.github.io` 的 Discussions。
giscus 分类接口已返回 Announcements 等六个分类，确认现有 giscus 安装可访问。
当前真实 ID 为：

- Repository：`MDEwOlJlcG9zaXRvcnkzMTM0ODIyMzc=`
- Announcements：`DIC_kwDOEq9b_c4DFFLD`

此前 Discussions 未开启，分类列表为空，旧模板中的仓库和分类 ID 也不正确。

在 [Settings → General → Features](https://github.com/wxxlamp/wxxlamp.github.io/settings)
保持 **Discussions** 开启，并保留 **Announcements** 分类。
如采用其他分类，在 `themes/wxx-theme/_config.yml` 的 `giscus.category` 和
`giscus.category_id` 中填入其准确名称及 ID。

已通过 [giscus 分类接口](https://giscus.app/api/discussions/categories?repo=wxxlamp%2Fwxxlamp.github.io)
核验并将真实仓库与分类 ID 写入主题配置。该接口不允许博客 origin 跨域访问，
所以浏览器不再动态查询分类，而是直接加载 giscus 官方客户端。
配置 ID 缺失或客户端脚本加载失败时显示提示和重试按钮。
仍使用原来的 `pathname` 映射，中文页面用中文评论界面，英文页面用英文。

启用后可在 [giscus 官方配置页](https://giscus.app/zh-CN) 核验仓库及分类，
随后在部署后的文章页验证一次真实评论。仅看到评论框不代表已验证写入成功。

本次本地联调已显示 `0 comments`、Write/Preview 和 GitHub 登录入口；
包含 Umami 接入的 23 项测试通过。尚未发表测试评论，线上写入待发布后验证。
