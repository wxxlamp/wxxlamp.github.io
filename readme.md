# 王星星的魔灯

个人技术博客，记录技术成长与生活感悟。

- **地址**: https://wxxlamp.cn
- **平台**: GitHub Pages
- **构建工具**: Hexo 8.x
- **主题**: wxx-theme（基于 polarbear 深度定制）

## 特性

- **移动端响应式**: 单行 header、触控友好导航、sidebar 自适应、多断点适配（768px / 480px / 375px）
- **中国访问优化**: 移除 Google Fonts（大陆被墙），Smiley Sans 字体异步加载，系统字体栈兜底
- **固定 Header + 侧边栏**: 桌面端固定导航和 Tags/Categories 侧边栏，移动端自动折叠
- **双语简历**: 支持中文/英文简历切换，带密码保护和 PDF 导出
- **TOC 目录**: 文章页自动生成目录，固定在右侧（桌面端 > 1200px）
- **RSS 订阅**: Atom 格式，集成在导航栏
- **访问统计**: Busuanzi 访客计数
- **阅读进度条**: 文章页顶部渐变进度指示

## 分支说明

| 分支 | 用途 |
|------|------|
| `deploy` | 源码分支 — Hexo 源文件（Markdown、配置、主题） |
| `main` | 部署分支 — GitHub Actions 生成的静态 HTML |

> **注意**: 不要手动向 `main` 分支推送代码，该分支由 GitHub Actions 自动维护。

## 本地开发

```bash
# 安装依赖
npm install

# 启动本地服务器（默认 http://localhost:4000）
npm run server

# 生成静态文件
npm run build

# 清理缓存和生成文件
npm run clean
```

## 写作

```bash
hexo new "文章标题"
```

文章存放在 `source/_posts/`，支持以下 Front Matter：

```yaml
---
title: 文章标题
date: YYYY-MM-DD HH:mm:ss
tags:
  - 标签1
categories:
  - 分类1
---
```

## 部署流程

推送到 `deploy` 分支后，GitHub Actions 自动完成：

1. 安装依赖并执行 `hexo generate`
2. 将 `public/` 部署到 `main` 分支
3. GitHub Pages 从 `main` 分支提供服务

## 目录结构

```
├── _config.yml              # Hexo 主配置
├── package.json             # 项目依赖
├── source/                  # 博客内容
│   ├── _posts/              # Markdown 文章
│   ├── about/               # 关于页面
│   ├── resume/              # 简历页面（中文/英文）
│   ├── favicon.ico          # 自定义网站图标
│   └── CNAME                # 自定义域名配置
├── themes/wxx-theme/        # 当前主题
│   ├── _config.yml          # 主题配置（菜单、小部件、配色）
│   ├── layout/              # Swig 模板
│   └── source/css/          # SCSS 样式
│       ├── _variables.scss  # 全局变量和断点
│       └── _custom/custom.scss  # 自定义响应式样式
├── scaffolds/               # 文章模板
└── .github/workflows/       # CI/CD 配置
```

## 主题开发

核心样式文件: `themes/wxx-theme/source/css/_custom/custom.scss`

- 响应式断点: 768px（平板）、480px（手机）、375px（小屏手机）
- 字体: Smiley Sans Oblique（异步加载）+ 系统字体栈
- 配色主题: 通过 `themes/wxx-theme/_config.yml` 的 `theme.color` 配置

## TODO

1. 语雀自动拉取文章
2. 拉取后生成 md 文件，并对内容图片进行上传、生成封面、描述等
3. 然后自动 commit

## License

MIT
