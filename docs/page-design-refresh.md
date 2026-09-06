# 页面设计优化

分支：`codex/page-design-refresh`。

## 设计与维护

- 暖白底色、绿色强调、系统正文字体；首页引言使用本地宋体 / Georgia。
- 页面共用 1120px 容器、流动边距和统一字号层级。文章正文最多 760px；首页侧栏使用 Grid，700px 以下移到列表下方。
- 顶部导航使用 sticky；手机导航分为两行，不依赖悬浮菜单。目录在 960px 以下可折叠，代码和表格在自身区域横向滚动。
- 设计变量和响应式规则在 `themes/wxx-theme/source/css/_custom/custom.scss`。不要再为每个设备追加一套覆盖规则。
- 移除外部装饰字体请求；MathJax 仅在文章或显式设置 `mathjax: true` 的页面加载。

## 精选英文内容与订阅

首页主标题为「勇士斗恶龙」。英文版使用独立的站内页面，包含 47 篇精选原创工程实践、架构 / AI、业务和成长文章；面经、刷题、教资备考等 41 篇保留中文。英文 Markdown 位于 `source/_posts/en/`，与中文原稿同名，通过 `lang: en` 和 `translation_of` 配对。没有 Google 翻译提示、外部翻译跳转或运行时翻译 API。

中英文内容使用真实链接切换。只在存在对应译稿 / 路由时显示 EN。英文首页、归档、分类、标签和上下篇仅包含精选译稿，标签与分类显示英文名称；中文列表保持原来的 88 篇。维护方式见 [双语内容维护](bilingual-content.md)。

RSS 修复了原来订阅源缺少正文、图标地址错误的问题。Atom 明确声明 HTML 内容，RSS 2.0 提供完整正文，代码换行保留，文章图片和链接转为绝对地址。四个订阅源分别为 `/atom.xml`、`/rss.xml`、`/en/atom.xml`、`/en/rss.xml`，各包含最近 20 篇对应语言的文章。`/subscribe/` 与 `/en/subscribe/` 提供订阅地址及复制按钮。

中英文简历继续使用既有译文，直接切换对应页面。

## 简历与打印

`resume-en.swig` 复用 `resume.swig`，文字内容继续分别维护在 `source/resume/index.md` 与 `source/resume-en/index.md`。本次不改写履历内容，保留原有每月访问密码及缓存行为。

`source/css/resume.scss` 使用独立打印样式：A4、上下 14mm / 左右 15mm 边距、10pt 正文；移除工具栏、导航和背景。标题与后续内容保持相连，项目简介和单条要点尽量不拆页，整个长项目允许自然分页。

打印设置建议：A4、100% 缩放、关闭浏览器页眉页脚。完整内容在 Chrome 中中文 2 页、英文 3 页；其他浏览器和字体环境的分页可能略有不同。

## 验证

- `npm run build`：成功；仍有主题原有的 Sass 弃用提示。
- `npm test`：14 项测试通过，覆盖 RSS 正文、链接、更新时间，以及 Markdown 公式、代码和货币符号的区分。
- `npm run check:translations`：47 篇译稿通过元数据、章节层级、代码块、图片和链接完整性检查。
- `python3 tools/check-generated-site.py`：335 个 HTML 页面、47 对中英文文章、41 篇中文文章及四个全文订阅源通过检查，站内绝对路径无缺失，CNAME 保持 `wxxlamp.cn`。
- 浏览器检查手机和桌面的首页、英文文章与订阅页、语言切换、章节目录及复制订阅地址。
- 之前已检查关于、归档、中英文简历、密码失败与解锁缓存行为；中英文简历 PDF 分别 2 页和 3 页，并逐页检查。

本轮优化从 `codex/page-design-refresh` 合入源码分支 `deploy`；发布仍由用户推送后触发 GitHub Actions。原工作区已有的公众号、小红书内容保持不变。


## 内容与视觉第二轮

- 全部 88 篇中文和 47 篇英文文章标题改为专业、清晰的表达；逐篇标题与归类可查看 [文章目录](content-catalog.md)。slug 与发布日期保持不变，正文只修复 AI/ML 失效封面链接。
- 分类与话题统一读取 `source/_data/taxonomy.json`，包含 9 个分类、34 个核心话题。每篇一个分类、1–3 个话题，显示名按语言映射；区块链并入基础夯实，列表按该语言文章数降序排列。
- 首页英文口号为 Warrior Fights Dragons。关于页中英文重写，取消重复页面标题，保留导航入口。
- 网站图标为绿色灯笼，SVG、ICO、PNG 与 Apple Touch Icon 使用相同图形。导航辅助图标统一为 SVG 线条图标，移除图标字体依赖。
- 正文 h1–h6 使用不同强调色。MathJax 3.2.2 本地托管，Markdown 扩展保护公式中的下划线、反斜线与矩阵换行，兼容旧文单美元多行写法。
- AI/ML 中英文文章各 57 处公式渲染成功，无 MathJax 错误；375px 手机整页无横向溢出，长公式区域可独立滚动。桌面与手机关于页、双语分类/话题显示已检查。

## 插件部署记录

语雀多平台发布插件已更新至 `0.4.0+codex.20260905183615`，本地个人插件安装成功，17 个改动文件与安装缓存一致。33 项插件测试、插件清单和 Skill 验证通过。已发布至 `wxxlamp/ai-coding-config` 的 main 分支，提交 [e994d8a](https://github.com/wxxlamp/ai-coding-config/commit/e994d8aa62262c05f2b63493356e856007f0041a)，仅修改目标插件目录。新建 Codex 任务后加载新版 Skill。


## 引用语言与简短个人简介

补译 Hexo 入门、@RequestBody、Java 内存和 2024 年回顾，英文文章共 47 篇。所有站内文章引用使用对应语言的真实页面；macOS 旧地址已修复，正文参考文档使用已核验的同语言版本。无英文译版的外部中文原始资料保留出处并标注 in Chinese，不替换成内容不同的文章。

`source/_data/references.json` 保存已核验的双语外部链接、旧路由和来源语言；`tools/check-references.py` 检查正文、HTML 和裸链接，`tools/check-translations.cjs` 接受中英同源引用的等价 URL。生成站点检查同时覆盖绝对站内链接。

关于页精简为教育、工作、兴趣与联系方式，补充两段实习时间，学校和机构附官方入口。当前聚焦金融与 AI Agent，未来重点为 AI Agent。


### 引用校验插件发布状态

本地已安装 `0.4.0+codex.20260905191729`，41 项插件测试通过。用户明确授权发布后，提交 [22f4678](https://github.com/wxxlamp/ai-coding-config/commit/22f467853d5de6237bb62ee4173389082898cb75) 已成功发布至目标仓库 main 分支，并核验远端版本与本地安装一致。

## 英文品牌与 SEO

英文姓名统一为 Sibo Wang，站点名统一为 Sibo's Blog，覆盖导航、页脚、简历、订阅源和搜索元数据。关于页采用无小标题的自然段，附学校及机构官方链接、联系方式、公众号「王星星的魔灯」二维码与小红书主页。

SEO 由 `lib/site-seo.js` 和 `scripts/site-seo.js` 统一生成：每页唯一标题、描述和 canonical，双语互指 hreflang 与 x-default，BlogPosting / AboutPage / WebSite 等 JSON-LD，Open Graph 与 Twitter 分享元数据。英文界面文字在生成时写入 HTML，搜索引擎无需执行 JavaScript 即可读取。

构建自动生成 `sitemap.xml` 与 `robots.txt`。简历页面保留 noindex，排除在站点地图之外；不使用构建时间伪造文章更新时间。分类、话题、分页和月份归档使用可区分的标题。`npm run check:seo` 核验 335 个页面、333 个站点地图 URL、双语链接、英文品牌和结构化数据。

网站发布后可在 Google Search Console 提交 https://wxxlamp.cn/sitemap.xml；当前仅完成本地优化，网站尚未推送。实现参考 Google 官方的[多语言页面](https://developers.google.com/search/docs/specialty/international/localized-versions)、[站点地图](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)与[文章结构化数据](https://developers.google.com/search/docs/appearance/structured-data/article)文档。


## 最终页面细节

关于页的教育和工作经历按最近到最早排列，公众号图片居中；国际化、AI Agent、金融方向附对应语言的博客链接。中英文简历顶部仅保留居中的姓名和联系方式，各项目末尾提供相关实践链接，PDF 导出保留可点击的正式域名 URL；已确认中文 2 页、英文 3 页。

手机导航采用四个等宽居中入口及 44px 点击高度，当前页面以浅绿色背景标识。页脚移除旧版 1000px 宽度限制，分隔线铺满页面，内部内容与页眉对齐。`/design-history/` 提供 7 个旧版静态页面的新旧对照，详见 [快照维护说明](design-history.md)。
