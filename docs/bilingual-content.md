# 精选英文文章

中文稿件仍在 `source/_posts/<slug>.md`。仅为值得向英文读者介绍的文章维护 `source/_posts/en/<slug>.md`：优先原创工程实践、架构 / AI 思考、业务分析与有代表性的成长文章，不默认翻译所有文章；面经、刷题、教资备考不在当前精选范围内。

## 新增或更新译稿

1. 在 `source/_posts/en/` 新建与原文同名的 Markdown 文件。
2. 翻译标题、描述及完整正文；保留代码块原样，保留图片 / 参考链接、章节顺序与层级。日期、分类、标签复制原值，分类和标签的英文显示名由主题统一映射。
3. 增加配对元数据，例如：

```yaml
---
title: Building and Testing a Distributed Lock
date: 2024-06-15 18:39
tags:
  - JAVA
  - 分布式
  - 系统设计
categories:
  - 架构思考
description: A practical look at implementing and testing a distributed lock.
lang: en
translation_of: distributed-lock-implementation
---
```

4. 运行 `npm run check:translations`，然后 `npm run build`。运行 `python3 tools/check-generated-site.py` 检查生成页面与 RSS。
5. 如果开发服务器已经启动，修改英文稿后重启 `npm run server`。`_posts/en` 被 Hexo 默认内容处理器忽略，由自定义生成器读取，因此不会通过普通 Markdown watch 自动更新。

译稿是本地静态文件，无翻译服务、API Key 或后续按次费用。代码注释和图片内的中文保持原样；译文不对历史文章的事实与技术结论做额外更新。

## 路由与选择规则

- 中文：`/YYYY/MM/DD/<slug>/`；英文：`/en/YYYY/MM/DD/<slug>/`。
- `scripts/localized-content.js` 根据实际存在的译稿生成英文首页、归档、分类、标签和相邻文章导航。没有译稿的文章只显示中文入口。
- 英文首页、各分类及标签的数量按精选译稿计算，空分类不显示。
- 原文章已有的章节 ID 在英文版中保留，便于跨语言分享章节链接。
- `hreflang` 仅为真实存在的中英文页面配对。`canonical` 指向各自的正式 URL。
- 撤下某篇英文译稿后，执行 `npm run clean` 和 `npm run build` 清除旧生成路由。

## RSS

`lib/blog-feeds.js` 生成中英各两种全文订阅源，并替代原 feed 插件的正文输出：

| 内容 | Atom | RSS 2.0 |
| --- | --- | --- |
| 中文全部文章 | `/atom.xml` | `/rss.xml` |
| 英文精选文章 | `/en/atom.xml` | `/en/rss.xml` |

每个源包含对应语言最新 20 篇文章。中文订阅 ID / 文章 URL 保持原地址；英文源使用独立 URL。正文保留 HTML 与代码换行，图片和相对链接转为绝对地址。网页为当前语言提供两条订阅发现链接，订阅入口页支持复制地址。


## 标题与话题维护

中文、英文文章标题各自保持专业清晰，避免营销式表达。规范分类和话题由 `source/_data/taxonomy.json` 维护，front matter 统一使用中文规范名，模板映射英文显示；每篇一个分类、1–3 个核心话题。目录见 [文章目录](content-catalog.md)。

语雀多平台发布插件的新项目读取同一目录，通过 `publishing-context` 获取指纹。AI 根据文章完整性、工程复用价值和国际读者收益决定是否生成英文，面试等内容通常跳过；需要英文时同步生成正文与英文配图，并纳入复审。详见插件 `references/publishing-plan.md`。


## 引用语言与简短个人简介

补译 Hexo 入门、@RequestBody、Java 内存和 2024 年回顾，英文文章共 47 篇。所有站内文章引用使用对应语言的真实页面；macOS 旧地址已修复，正文参考文档使用已核验的同语言版本。无英文译版的外部中文原始资料保留出处并标注 in Chinese，不替换成内容不同的文章。

`source/_data/references.json` 保存已核验的双语外部链接、旧路由和来源语言；`tools/check-references.py` 检查正文、HTML 和裸链接，`tools/check-translations.cjs` 接受中英同源引用的等价 URL。生成站点检查同时覆盖绝对站内链接。

关于页精简为教育、工作、兴趣与联系方式，补充两段实习时间，学校和机构附官方入口。当前聚焦金融与 AI Agent，未来重点为 AI Agent。
