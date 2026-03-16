---
title: "漫谈JavaFX"
date: 2021-10-31 19:52
tags:
   - Java
   - JavaFX
categories:
   - 基础夯实
description: "作者因一个桌面工具小需求而试用JavaFX，本文系统介绍了JavaFX的核心特性（FXML布局、CSS样式、数据绑定、Native Compiling）与Stage/Scene/Nodes设计模型，并给出快速上手步骤。在工程化层面，作者坦率指出JavaFX的三大短板：组件化体系落后导致复用和通信困难、FXML动态渲染能力不足、生态薄弱需要大量造轮子，并与前端JavaScript生态进行对比。文章最后梳理大前端各平台主流技术栈，从界面构建的本质视角统一理解前端开发。"
---

从接触软件工程到现在，我依次使用过C/Cpp/Java/Php/Python/JavaScript等编程语言，也使用过它们的一些工程化的框架，如Java系的Spring，Js系的Vue和React。因为机缘巧合，我对Java接触的更多一点，用Spring写过Web，用Jsoup写过爬虫，用Swing写过桌面，用Netty写过IM，恰好最近有一个开发桌面端工具的小需求，所以就试用了一把号称`next generation client application platform for desktop, mobile and embedded systems based on JavaSE` 的JavaFX


本文会着重说明JavaFx针对于使用者的设计思路，同时也会用少量的笔墨比较下和前端生态的不同 : )


### JavaFX简介


#### 特点


1. 采用Fxml进行UI界面的搭建（类似于Html）
1. 采用CSS对组件进行样式填充（当然也可以通过硬编码）
1. 可以通过WebView运行JavaScript代码
1. 丰富的内置组件，如HtmlEditor，TreeView等等，同时也可以自定义组件
1. 支持数据绑定，UI线程刷新界面的时候可以直接获取到最新的数据
1. Native Compiling，意味着不用再要求客户安装JRE了

#### 设计模型


对于JavaFx来说，有几个重要的组件。如Stage，Scene，Nodes。Stage对应着窗口，主界面是一个Stage，提示弹窗也是一个Stage。Scene指的是页面，在一个Stage中，可以有多个Scene。Nodes指的是组件，node可以根据不同的布局嵌入到scene中


对于Nodes来说，有以下三种类型：


- Root Node：第一个场景视图
- Branch Node：具有子节点的节点，主要有Group，Region(Pane/Control)，WebView
- Leaf Node：没有子节点的节点，如Button，ImageView

<center><img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/c94bddd1_javafx.png" alt="JavaFX" style="zoom: 67%;"/></center>

### 快速上手


那么，要编写一个简单的桌面应用，并且需要利用JavaFx的各种牛逼特性，需要几步呢？


1. 通过IDE新建一个JavaFX项目
1. 使用SenceBuilder配置组件布局并生成Fxml文件
1. 使用CSS对组件样式进行填充
1. 将Controller和Fxml中的组件关联起来，在Controller中配置组件的属性，以及组件相关事件的响应逻辑
1. 在Controller中完成对应业务逻辑的处理
1. 通过IDEA的打包工具对JavaFX项目进行Native Compiling，声称对应的客户端文件(exe/dmg)

具体的步骤可以参考[JavaFx教程](https://code.makery.ch/zh-cn/library/javafx-tutorial/part1/)


**【注意】因为从JDK9开始，FX项目就从JDK自带的类库中移除，所以新手建议使用JDK8，如果使用JDK9+则需要进行相关的模块化配置，并且引入JavaFX的Jar包**


### 工程化


#### 窗体缩放


客户端的窗体往往需要缩放，那么，设计者就必须考虑窗体在缩放时，组件的大小变化，以及组件相对位置和绝对位置的变化，针对于这些问题，我们可以通过布局和双向绑定来解决


1. 通过`AnchorPane` 固定组件在窗体中的位置，这样组件就会对窗体的Width&Height变化无感知
1. 通过组件的数据绑定功能，将组件的大小以及相对距离与窗体的Width&Height绑定到一起，然后当窗体变化的时候，组件被绑定的相关信息也会变化

#### 现有问题


JavaFx作为Demo来用是完全合格的，但是它想称霸桌面开发，我觉得从工程化的层面上来讲，还有很多的问题，尤其是跟当前的前端生态相比，还差了许多。下面简单列举一下我在开发JavaFx的过程中遇到的一些问题


1. 组件化建设很落后，意味着很难复用，并且组件通信是一个大问题。当然，这不是说JavaFX不能进行组件通信，我只是说JavaFX的组件通信需要用户自己完善，很难支持大型项目开发。举个例子，假设sence中的button接收到了click event后，需要读取其他Sence中各个组件的信息，这对于JavaFX就很难搞，如果有很多类似需求，那么将会很快的腐蚀掉已有的代码
1. 简单的界面和逻辑分离，没办法动态加载组件。JavaFX当前的FXML编程模型，只能跟20年前使用HTML+CSS+JavaScript编写网页的状态一样。一个简单的栗子：有一个boolean变量a，假如用户希望a=true的时候当前界面渲染button，反之，当前界面渲染textArea。这个需求很简单，也很常见，JavaScript生态中的各个框架(Vue/React/...)都能很简单的实现，但是，对于JavaFX来说，如果你是用Fxml进行页面渲染，这将需要更多的代码量才能完成
1. 生态太弱，需要一些基础能力都需要自己造轮子。JavaFX跟JavaScript的生态相比，差的不是一点两点，需要数十年才能赶平，当然，我觉得JavaFX是没希望了追上JavaScript的生态了，毕竟用JavaFX的人少，生态也很难好好发展起来



**【当然，这都是我一家之言，也可能JavaFX在lastest version中已经完善，要是有人有解决方案可以留言】**


### 漫谈大前端


如今的大前端百花齐放，先梳理下各个平台用到的开发工具：


- Web和H5领域：主要是JavaScrpit和TypeScript，使用的框架一般是Vue/React/Angular
- IOS领域：主要用Swift/Object-C
- Android领域：主要是Java/Kotlin
- PC领域:：如果是Windows的话可以用C#，如果是Mac的话可以用Swift
- 跨平台领域：有JavaScript(Electron)，Java(FX)，Dart(Flutter)，Cpp(QT)



什么是前端，我理解的前端就是直接跟用户交互的平台，抽象来说，就是界面+逻辑


如果要编写一个界面，我们需要定义这个界面的骨架和布局，即我们需要规定好当前界面或模块中，每个组件的排列方式，常见的布局方式有浮动布局，绝对定位布局，网格布局，弹性布局等等。有了布局之后，我们就需要将组件放在布局上，常见的组件有form，button，table等等。通过布局+组件的结合，就形成了基本的用户界面。但是，这样还远远不够，因为组件没有样式，如果想要红的button，绿的form，紫的table，就需要再进行样式填充，给予组件五彩斑斓的黑


对于前端来讲，仅仅编写完界面只是是第一步，更重要的是逻辑的编写。譬如组件展示的时机，触发组件后的反馈效果，路由能力的编写等等。随着前后端分离的热潮，前端越来越重要，不仅包含一些业务逻辑，也有各种抽象和逻辑服用，这会使得逻辑代码的编写更加复杂


所以，无论是H5还是客户端，对于前端来讲，编写一个界面需要布局+组件+样式，其中用到的语言工具无非是HTML/XML/FXML+CSS。然后我们再通过编程语言（JavaScript/Java/Cpp/...）来赋予界面行为和业务逻辑，便可以构建五彩缤纷的前端世界
