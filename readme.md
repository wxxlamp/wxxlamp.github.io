# 王星星的魔灯

个人技术博客，记录技术成长与生活感悟。

- **地址**: https://wxxlamp.cn
- **平台**: GitHub Pages
- **构建工具**: Hexo 8.x
- **主题**: wxx-theme（基于 polarbear 深度定制，支持移动端优化）

## 分支说明

| 分支 | 用途 |
|------|------|
| `deploy` | 源码分支，存放 Hexo 源文件（Markdown、配置、主题） |
| `main` | 部署分支，存放 GitHub Actions 生成的静态 HTML |
| `test` | 开发分支，用于测试主题变更 |

> **注意**：不要手动向 `main` 分支推送代码，该分支由 GitHub Actions 自动维护。

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
# 新建文章
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

推送到 `deploy` 分支后，GitHub Actions 自动完成以下步骤：

1. 安装依赖
2. 执行 `hexo generate` 生成静态文件
3. 将 `public/` 目录内容部署到 `main` 分支
4. GitHub Pages 从 `main` 分支提供服务

## 目录结构

```
├── _config.yml              # Hexo 主配置
├── package.json             # 项目依赖
├── source/                  # 博客内容
│   ├── _posts/              # Markdown 文章
│   ├── about/               # 关于页面
│   ├── resume/              # 简历页面
│   └── CNAME                # 自定义域名配置
├── themes/
│   └── wxx-theme/           # 当前主题
├── scaffolds/               # 文章模板
└── .github/workflows/       # CI/CD 配置
```

## TODO

1. 语雀自动拉取文章
2. 拉取后生成 md 文件，并对内容图片进行上传、生成封面、描述等
3. 然后自动 commit

## License

MIT
