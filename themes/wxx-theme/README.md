# WXX Theme

为「王星星的魔灯」自主设计维护的 Hexo 主题。围绕技术长文、双语写作和个人资料展示，采用暖白底色、墨绿强调色与简洁的阅读布局。

[在线预览](https://wxxlamp.cn) · [项目运行与部署说明](../../readme.md)

## 设计与功能

### 阅读体验

首页以文章列表展示标题、摘要和元信息，侧栏提供作者介绍、分类、标签与订阅入口。文章页突出正文，配合章节目录、当前位置高亮、阅读进度与回到顶部。

正文使用系统字体栈，标题、引用、代码、表格和图片各有对应样式；首页介绍使用衬线字体。图标采用内联 SVG，公式通过本地 MathJax 资源渲染。

### 响应式布局

粘性顶栏保持导航可达。桌面端文章目录位于正文侧面，小屏设备转为可折叠目录；资料页提供可收起的桌面目录和移动端抽屉导航。代码与表格可横向滚动，简历具有独立打印样式。

### 双语内容

中文与英文页面使用独立 URL，英文站位于 `/en/`。主题根据页面语言显示导航、分类标签和订阅入口，存在对应译文时提供语言切换。中文资料库入口不出现在英文导航中；简历使用 `/resume/` 与 `/resume-en/`。

翻译内容、路由和语言辅助函数由仓库根目录 `scripts/localized-content.js` 提供，分类与标签译名来自 `source/_data/taxonomy.json`。

### 内容与服务

- 文章、归档、分类、标签、关于与订阅页面。
- 基于清单生成的课程资料库。
- 带访问口令界面的双语简历及打印 / PDF 导出。
- 中英文独立的 Atom / RSS 全文订阅与订阅地址复制。
- GitHub Discussions / Giscus 评论。
- 自托管 Umami 可见访问计数，以及配置中的其他分析服务。
- canonical、语言元信息、结构化数据与站点地图。

## 使用方式

主题随本仓库源码一起维护，依赖根目录 `scripts/`、`lib/` 和 `source/_data/` 中的扩展与数据。复用时应从完整项目开始；仅复制主题目录不足以运行全部功能。

根目录 `_config.yml` 已启用：

```yaml
theme: wxx-theme
```

在项目根目录使用 Node.js 22：

```bash
npm install
npm run server
npm run build
```

发布流程为：源码推送到 `deploy` → GitHub Actions 构建 → 静态文件写入 `main` → GitHub Pages 提供服务。分支、权限和自定义域名设置见[项目部署说明](../../readme.md#部署)。

## 开发入口

| 位置 | 用途 |
| --- | --- |
| `layout/_layout.swig` | 通用页面骨架 |
| `layout/_partial/header.swig` | 导航、当前语言入口 |
| `layout/index.swig`、`layout/post.swig` | 首页与文章布局 |
| `layout/resource-doc.swig` | 资料正文与导航布局 |
| `layout/resume.swig` | 双语简历共用模板 |
| `source/css/style.scss` | 主样式入口 |
| `source/css/_custom/custom.scss` | 当前视觉系统、组件与响应式规则 |
| `source/css/resume.scss` | 简历与打印样式 |
| `source/js/src/site.js` | 语言界面、目录、阅读进度及资料导航 |
| `_config.yml` | 评论、统计等服务设置 |

### 配色与排版

当前视觉样式集中在 `source/css/_custom/custom.scss`，主要使用 CSS 自定义属性：

```css
:root {
  --paper: #faf9f6;
  --surface: #fff;
  --ink: #252c29;
  --muted: #68716b;
  --accent: #376451;
  --line: #e2e5de;
  --soft: #edf1e9;
  --page-width: 1120px;
  --gutter: clamp(20px, 4vw, 48px);
}
```

修改颜色、正文宽度或间距时优先调整这些变量。主题目录仍保留部分旧样式和配置项；当前导航、侧栏与主色应以实际模板和上述样式为准，不应依赖旧的 `menu`、`widget` 或 `theme.color` 配置来调整整个界面。

### 服务配置

`_config.yml` 中的 `giscus` 用于评论仓库与讨论分类；`umami` 用于统计脚本、站点标识及公开计数接口，`busuanzi` 独立控制不蒜子采集。复用项目时需替换为自己的服务配置，或关闭对应服务；不要在前端配置中写入私密密钥。

## 验证

先运行 `npm run build`，再通过 `npm run server` 预览首页、文章、资料页与双语简历。检查中英文切换、窄屏导航、目录、订阅复制及打印效果。

修改内容生成或服务逻辑后，在项目根目录运行 `npm test`，并按改动范围执行 `npm run check:translations` 或 `npm run check:seo`。

## 许可证

主题代码采用 [MIT License](LICENSE)，版权与许可声明见许可证文件。
