# 王星星的魔灯

记录技术成长与生活感悟的个人博客，使用 Hexo 8 和自主设计维护的 **WXX Theme**，通过 GitHub Actions 构建并发布到 GitHub Pages。

[访问博客](https://wxxlamp.cn) · [English](https://wxxlamp.cn/en/) · [订阅更新](https://wxxlamp.cn/subscribe/)

## 主题特色

- **以阅读为中心的设计**：暖白底色、墨绿强调色、留白与细分隔线；首页采用文章列表与探索侧栏，文章页为正文与目录布局。
- **响应式体验**：粘性顶栏、适配小屏的导航与排版；文章目录在移动端可折叠，代码与表格支持横向滚动。
- **站内搜索**：按语言隔离索引，支持标题、正文与代码、分类和标签搜索，提供部分匹配、多关键词、英文单字符拼写容错；中文另包含资料和关于等公开页面，双语简历均不索引。
- **中英文内容**：中文站与 `/en/` 英文站独立生成，包含文章、归档、分类、标签、关于和订阅页面；有对应译文时提供语言切换。资料入口仅在中文界面显示。
- **长文与技术写作**：目录定位与当前章节高亮、阅读进度、回到顶部、代码高亮，以及本地 MathJax 公式渲染。
- **资料库**：课程资料按清单生成独立页面，桌面端目录可收起，移动端使用抽屉导航。
- **双语简历**：中文与英文简历共用版式，提供访问口令界面、打印样式和浏览器另存为 PDF。
- **订阅与互动**：中英文各自提供 Atom / RSS 全文订阅，订阅页可复制地址，文章评论使用 GitHub Discussions / Giscus。
- **搜索与统计基础**：语言对应的元信息、canonical、结构化数据与站点地图；展示自托管 Umami 访问统计，并接入配置中的分析服务。
- **轻量界面资源**：正文采用系统字体栈，图标使用内联 SVG，无需额外图标字体。

主题实现与修改入口见 [主题说明](themes/wxx-theme/README.md)。

## 本地运行

使用 Node.js 22，与 CI 环境保持一致。

```bash
npm install
npm run server
```

打开 `http://localhost:4000` 预览。

| 命令 | 用途 |
| --- | --- |
| `npm run server` | 启动本地预览 |
| `npm run build` | 生成站点到 `public/` |
| `npm run clean` | 清理缓存与生成文件 |
| `npm test` | 检查订阅、SEO、统计、组件与公式等逻辑 |
| `npm run check:translations` | 检查译文元数据、结构与引用 |
| `npm run check:seo` | 检查已生成页面的 SEO 信息，需先构建 |

## 内容维护

### 文章

```bash
npx hexo new "文章标题"
```

文章保存在 `source/_posts/`，示例：

```yaml
---
title: 文章标题
date: 2026-09-26 10:00:00
description: 用一段简短文字介绍文章内容。
tags:
  - Java
categories:
  - 技术学习
---
```

### 英文译文

在 `source/_posts/en/` 添加与原文同名的 Markdown 文件，并声明：

```yaml
---
title: Article title
lang: en
translation_of: original-post-slug
description: A short introduction to the article.
---
```

`translation_of` 对应中文原文文件名，不包含 `.md`。日期与分类、标签由原文关联；分类和标签的英文名称由 `source/_data/taxonomy.json` 维护。英文内容由 `scripts/localized-content.js` 单独生成，无译文的文章不会自动翻译。

### 资料与独立页面

- 资料入口与概览：`source/resources/`。
- 课程资料清单：`source/_data/hkust-resources.json`，由 `scripts/resource-pages.js` 生成资料页面。
- 关于与订阅：`source/about/`、`source/subscribe/` 及对应英文页面。
- 双语简历：`source/resume/`、`source/resume-en/`。

## 部署

### 分支与发布路径

| 分支 | 内容 | 维护方式 |
| --- | --- | --- |
| `deploy` | Markdown、主题、配置与构建脚本 | 日常源码开发 |
| `main` | `public/` 中生成的静态站点 | GitHub Actions 自动更新 |

工作流定义在 [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)。向 `deploy` 分支推送后：

1. 检出源码，准备 Node.js 22 环境并安装依赖。
2. 执行 `npx hexo generate`。
3. 使用 `peaceiris/actions-gh-pages` 和 `GITHUB_TOKEN`，将 `public/` 发布到 `main`。
4. GitHub Pages 从 `main` 分支根目录提供站点服务。

本地预览与检查通过后，由维护者手动推送源码。不要手动维护或推送生成内容到 `main`，下次部署会覆盖该分支。

### 仓库与域名配置

- GitHub Pages 使用分支发布，来源设为 `main` 的根目录。
- 工作流使用的 `GITHUB_TOKEN` 需要有仓库内容写入权限。
- 当前站点地址在 `_config.yml` 的 `url` 中配置为 `https://wxxlamp.cn`。
- 自定义域名文件必须保存在 `source/CNAME`，构建时会复制到 `public/CNAME`；域名的 DNS 与 Pages 自定义域名设置需与之对应。
- 当前发布由 GitHub Actions 完成；`_config.yml` 未配置 Hexo deploy 适配器，`npm run deploy` 不是本项目的发布入口。

`public/`、`db.json` 和 `.deploy_git/` 属于生成产物，不应提交到源码分支。

## 项目结构

```text
├── _config.yml                 # Hexo 配置、域名、分页与渲染设置
├── source/
│   ├── _posts/                 # 中文文章，en/ 为英文译文
│   ├── _data/                  # 分类翻译、引用与资料清单
│   ├── resources/              # 资料入口与概览
│   ├── about/                  # 关于页面
│   ├── subscribe/              # 订阅页面
│   ├── en/                     # 英文独立页面
│   ├── resume/、resume-en/     # 双语简历
│   ├── design-history/         # 历史设计快照
│   └── CNAME                   # 自定义域名
├── themes/wxx-theme/           # WXX Theme 模板、样式与前端脚本
├── scripts/                    # 双语生成、SEO、资料页等 Hexo 扩展
├── lib/                        # 订阅、SEO、公式处理公共逻辑
├── tests/                      # 自动化测试
├── tools/                      # 翻译、SEO 与设计快照检查工具
└── .github/workflows/          # 自动构建与发布
```

## 修改主题

页面结构使用 Swig，样式使用 SCSS，交互使用原生 JavaScript。导航、布局与内容生成需要结合模板和根目录 `scripts/` 修改，不能仅通过主题配置文件完成。

常用入口：

- `themes/wxx-theme/layout/_partial/header.swig`：导航与语言切换。
- `themes/wxx-theme/source/css/_custom/custom.scss`：当前设计变量、排版与响应式规则。
- `themes/wxx-theme/source/css/resume.scss`：简历屏幕与打印样式。
- `themes/wxx-theme/source/js/src/site.js`：语言界面、目录、订阅复制与资料导航。
- `themes/wxx-theme/_config.yml`：Giscus、Umami 等服务配置。

修改后构建并本地预览，检查中英文页面、桌面与手机布局；涉及订阅、SEO 或内容生成时，运行对应检查命令。

### 搜索维护

构建时由 `scripts/site-search.js` 从公开页面生成 `search/zh.json` 和 `search/en.json`，浏览器首次打开搜索时只加载当前语言索引。索引范围与正文提取逻辑在 `lib/site-search.js` 中维护；PDF 资料仅检索名称、课程和简介，不提取 PDF 内文。多关键词以空格分隔，所有词都需匹配；标题、分类与标签匹配优先于正文。
