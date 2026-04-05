---
name: yuque-to-post
description: 将语雀文档下载并转换为 Hexo 博客文章，Claude 基于内容智能生成50字描述，自动添加 front matter 并保存到 source/_posts/
license: Apache-2.0
metadata:
  author: wxx
  version: "1.2"
---

# Yuque to Post Skill

此技能将语雀文档自动转换为 Hexo 博客文章。流程由 Claude 主导：下载文档 → 分析内容 → 智能生成描述 → 生成最终文章。

## 前置依赖

1. **yuque-fetcher 技能**: 用于下载语雀文档
   ```bash
   ls .claude/skills/yuque-fetcher/
   ```

2. **Python 3.7+**

## 工作流程

Claude 执行以下步骤：

### 步骤 1: 预览文档内容

使用 `--preview` 参数下载并查看文档内容：

```bash
python3 .claude/skills/yuque-to-post/yuque-to-post.py <yuque_url> --preview
```

这会输出：
- 文档标题
- 文档内容前 2000 字符

### 步骤 2: Claude 生成描述

基于输出的文档内容，Claude 智能生成一段 40-60 字的描述，要求：
- 准确概括文章核心内容
- 语言简洁、专业
- 不包含"本文"、"文章"等元话语

### 步骤 3: 生成博客文章

使用生成的描述执行脚本：

```bash
python3 .claude/skills/yuque-to-post/yuque-to-post.py <yuque_url> \
  --desc "Claude生成的描述" \
  --tags "标签1,标签2" \
  --categories "分类"
```

## 完整示例

```bash
# 第1步：预览内容
python3 .claude/skills/yuque-to-post/yuque-to-post.py \
  https://www.yuque.com/user/repo/slug \
  --preview

# 第2步：Claude 分析内容后生成描述...
# 例如："深入解析 Java 8 Stream API 的核心原理与使用技巧，包含常见操作示例与性能优化建议。"

# 第3步：生成文章
python3 .claude/skills/yuque-to-post/yuque-to-post.py \
  https://www.yuque.com/user/repo/slug \
  --desc "深入解析 Java 8 Stream API 的核心原理与使用技巧，包含常见操作示例与性能优化建议。" \
  --filename "java-stream-api-tutorial" \
  --tags "Java,Stream" \
  --categories "技术随笔"
```

## 参数说明

- `<yuque_url>`: 语雀文档 URL (必需)
- `--desc`: 文章描述 (必需，由 Claude 生成)
- `--filename`: 英文文件名，简短小写连字符格式，如 `my-blog-post` (默认使用标题转义，如果是中文标题则会尝试自动转换为英文)
- `--tags`: 文章标签，逗号分隔 (默认: 未分类)
- `--categories`: 文章分类，逗号分隔 (默认: 技术随笔)
- `--commit`: 生成后自动执行 `git add` 和 `git commit`
- `--preview`: 仅预览内容，不生成文件

## 文件名优化功能

当文档标题为中文时，技能会自动尝试将其转换为简短的英文文件名：
- "我的2025" → "my2025"
- "2025年目标达成情况" → "2025-year-goals-achievement-status"
- "技术分享心得" → "tech-share-insights"
- "年终总结" → "year-end-summary"

## 生成的 Front Matter 格式

```yaml
---
title: "文章标题"
date: 2026-04-05 17:04
tags:
   - 标签1
   - 标签2
categories:
   - 分类
description: "Claude生成的智能描述，约50字左右..."
---
```

## 注意事项

1. **首次使用 yuque-fetcher**: 会弹出浏览器窗口要求登录语雀
2. **描述生成**: 由 Claude 基于文档内容智能生成，非简单提取
3. **文件名**: 优先使用英文文件名以提升SEO友好性；如未指定 --filename 参数，将尝试从中文标题自动生成英文文件名
4. **图片**: 通过 yuque-fetcher 自动处理并上传到图床
