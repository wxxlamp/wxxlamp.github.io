---
title: A Practical Guide to Customizing Hexo Themes
date: 2021-03-22 19:38
tags:
  - 博客与写作
  - 开发工具
categories:
  - 采坑记录
description: >-
  An introduction to Hexo theme development, starting from Hexo’s workflow,
  analyzing theme components, and explaining how to add custom features such as
  categories, tables of contents, and statistics.
lang: en
translation_of: diy-hexo-theme
---

Why am I writing this article? As you can see, my blog is powered by Hexo and uses the [Anatole-core](https://github.com/mrcore/hexo-theme-Anatole-Core) theme. It is simple, attractive, and easy to use. Thanks to the author for open-sourcing it, resp.

However, some features of this theme did not meet my expectations. For example, it had no categories, table of contents, visitor statistics, donations, or friend links. Those direct needs drove me to modify the theme.

> PS: If you only want to use HEXO to write a blog, I recommend reading [this article](https://wxxlamp.cn/en/2020/12/16/hexo-guide/).

### 1. [How HEXO Works (in Chinese)](https://www.larscheng.com/hexo-principle/)

In HEXO, we use the `hexo g` command to generate corresponding HTML pages from our Markdown files, then display those static pages through a server in the browser. Two things happen in this process. First, HEXO parses variables in the Markdown file (such as title, crete_time, content, and author.etc) and stores them in memory. Second, HEXO uses a template-rendering engine to render those in-memory variables and form an HTML file.

> Here I let my imagination run a little. Building a website is almost every programmer’s need. HEXO is convenient, but a backend programmer who DIYs a HEXO theme still has to learn many frontend concepts. So I wondered whether HEXO’s functionality could be implemented in Java. Java has template engines such as Thymeleaf that can directly generate HTML; we would only need to parse the Markdown variables.

After that, HEXO copies the rendered HTML files and everything in the themes/source folder except layout into public for the browser to display.

### 2. HEXO Theme Components

From the explanation above, the second step in HEXO—rendering various HTML files—is completed by the various themes.

Normally, an HTML page consists of CSS, JS, and HTML itself. Our HEXO theme needs these three as well. But how are the variables in our Markdown rendered into HTML? This brings us back to template engines. Common engines include jade (pug), swig (built into hexo), ejs, and haml. At compile time, they render data into the HTML pages we need. Thus a Hexo theme needs a template engine, CSS, and JS.

Many people find CSS troublesome, so they use SCSS, Stylus, or Less during development. Developers must compile SCSS or Less into CSS, however, because Hexo copies everything except the layout folder from themes/source into public. The rendered HTML then references the JS and CSS we declared.

We also need various images, so a Hexo theme contains .jpg/.png files. Sometimes we need special fonts, so font files are needed too. To support internationalization, we also need YAML files for definitions.

In summary, a Hexo theme needs a template engine, CSS, JS, images, fonts, and so on.

### 3. Modifying Your Hexo Theme

When modifying a theme, you generally first enter the themes/source/layout folder and examine the layout of the whole theme.

A normal theme structure is divided into these parts:

- The HTML `head` section
- The top navigation bar, nav
- The page header and footer
- The page sidebar
- The page body (where the article is displayed), main
- ......

If you want to modify or even create a Hexo theme in greater depth, [this blog post may help (in Chinese)](https://liuyib.github.io/2019/08/20/develop-hexo-theme-from-0-to-1/).
