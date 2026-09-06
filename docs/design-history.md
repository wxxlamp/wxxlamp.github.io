# 旧版页面快照

当前优化分支中的 `/design-history/` 是新旧页面对照入口，旧版位于 `/design-history/main/`。

来源为 `origin/main` 提交 `07cd3b79e5663181139be8b4efb5f5205d461cb5`（2026-08-19）。保留首页、归档、关于、Java 内存文章、2023 年回顾、中英文简历共 7 页；不切换、不修改或推送远端 main。

`source/design-history/main/manifest.json` 记录提交、页面及本地资源。HTML 中的旧版 CSS、JavaScript 和图标路径改写到快照目录。快照页面之间可以跳转；未保存的站内页面链接禁用。外部图片、字体、MathJax CDN 仍使用原地址，因此不是完全离线的档案。旧版统计、评论提交脚本已移除，简历仍保留原访问逻辑。

Hexo 的 `skip_render` 原样复制此目录，不套用新主题。对照页及快照均标记 `noindex, nofollow`，也不进入新版 sitemap。日常 SEO 和双语校验只检查当前网站，快照单独执行：

```sh
node tools/check-design-snapshot.cjs
```

以后需要增加另一份独立快照，可先读取目标版本，再运行 `node tools/save-design-snapshot.cjs <git-ref> <目录名>`。脚本拒绝覆盖已有快照；对照页需同步加入新版本入口。不要在已有快照中重新构建旧主题，以免改变历史内容。

网站仍按仓库原流程从 deploy 源码构建到 main；将本优化分支的源代码合入 deploy 后，快照会与新版一起发布。
