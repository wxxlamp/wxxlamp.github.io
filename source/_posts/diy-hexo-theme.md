---
title: "HEXO主题修改指北"
date: 2021-03-22 19:38
tags:
   - HEXO
categories:
   - 采坑记录
description: "介绍Hexo主题二次开发原理与实践，从Hexo工作流程出发，剖析主题构成要素，并说明如何添加分类、目录、统计等定制功能。"
---

为什么会写这篇文章呢？如你所见，我的博客使用hexo驱动，使用的主题是[Anatole-core](https://github.com/mrcore/hexo-theme-Anatole-Core)，它简洁美观，易于使用，感谢作者的开源，resp。

但是这个主题的某些功能并不能达到我的想象。譬如没有分类，没有目录，没有用户访问统计，没有打赏，没有友链等等...所以，我的直接需求驱动着我去修改这个主题

> PS: 如果你仅仅是使用HEXO写博客，我推荐你访问[这篇文章](https://wxxlamp.cn/2020/12/16/hexo-guide/)

### 1. [HEXO工作原理](https://www.larscheng.com/hexo-principle/)

在HEXO中，我们通过`hexo g`命令来将我们的md文件生成为对应的html页面，进而将这些html静态页面通过服务器展示到browser中，在这个过程中，我们要意识到两件事的发生，第一件事是HEXO解析md中的变量(如title,crete_time,content,author.etc)并存储在内存中，第二件事是，HEXO通过模板渲染引擎对内存中的变量进行渲染并形成HTML文件。

> 这里我脑洞大开了一下，因为建站几乎是每个程序员的需求，即使HEXO很方便，但是后端程序员使用HEXO进行主题DIY的时候还要接触大量的前端概念，所以我想，能不能用Java实现HEXO的功能，毕竟Java有Thymeleaf之类的可以直接生成HTML的模板引擎，所以我们只需要解析md的变量即可

之后，其实还有一件事，HEXO会把渲染后的HTML和文件和themes/source文件夹的中除了layout的文件全部拷贝到public中，供浏览器展示

### 2. HEXO主题构成
通过上面的介绍，我们应该会知道，HEXO中的第二步，即渲染为各式各样的HTML文件这一步，就是我们各式各样的主题完成的。

在正常情况下，一个HTML的页面是由CSS，JS和HTML本身组成的，那么对于我们的HEXO主题来说，我们也需要包括这三样，但是等等，我们的md里面的变量如何渲染进HTML中呢？这就要提到我们之前说过的模板引擎了，常见的模板引擎有jade(pug)，swig(hexo自带)，ejs，haml几种，他们把数据在编译时渲染成了我们需要的html页面。那么到现在来说，一个hexo主题就需要有模板引擎，css，js。

但是，很多人觉得css太费事，所以他们在开发的时候会使用scss，stylus或者less，不过，开发者必须把scss或者less编译为css，因为hexo会把themes/source文件夹中的除了layout文件夹的内容全部拷贝到了public文件夹中，这时候，渲染成的html会去引用我们声明的js和css。

同时，我们还需要各种图片，所以一个hexo主题中也会有.jpg/.png文件，有时候我们还需要特殊字体，所以我们还需要字体相关的文件。不仅如此，为了支持国际化，我们还需要有yml文件去定义。

综上所述，一个hexo主题需要有：模板引擎,css,js,img,font.etc

### 3. 修改你的hexo主题

一般我们修改主题的时候，首先就需要进入themes/source/layout文件夹，去查看整个主题的页面布局情况。

一般的主题结构会分为下面几个部分：

- HTML 的 `head` 部分
- 顶部导航栏 nav
- 页面头部、底部
- 页面侧边栏 siderbar
- 页面主体部分（显示文章的地方） main
- ......

如果你想要更深一步去修改乃至创建hexo主题，[这篇博客可能对你有帮助。。。](https://liuyib.github.io/2019/08/20/develop-hexo-theme-from-0-to-1/)