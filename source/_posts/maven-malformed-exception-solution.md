---
title: "问题现象"
date: 2026-04-05 18:30
tags:
   - Maven
   - Debug
   - Java
categories:
   - 采坑记录
description: "本文详细记录了一次Maven编译时遇到Malformed \\uxxxx异常的排查过程，通过分析堆栈、调试源码，最终定位到是本地Maven仓库中resolver-status.properties文件的编码问题，并提供了有效的解决方案。"
---

# 问题现象
笔者在一次需求迭代的时候，从仓库拉下来了一个分支，然后肌肉记忆般的使用mvn reimport重新sync其他的依赖。本来以为这个已经点了几千次的操作会像往常一样顺利加载依赖，然后进入我最开心的写代码环节。结果却出现了下面的异常：

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/70c01355_c527162f.png)

看到这个异常一脸懵逼，难道是新拉下来的分支pom文件的编码有问题？

伴随着这个怀疑，开始了问题排查之旅。

# 问题排查
## Step 1. 确认代码是否有问题
打开应用的pom文件，发现没有修改过。同时为了double check，将该分支在aone上重新部署，没有出现编译异常，说明远程仓库的代码没有问题，是自己环境的问题。

## Step 2. 确认是否是IDE问题
既然代码没有问题，那就可能是IDE的缓存导致的，所以将IDE的缓存进行清空并且restart。为了保险起见，还特意删除了应用本地的仓库，重新git clone。但是不幸的是，依然没有解决这个问题。

## Step 3. 确认是否是依赖问题
现在回过头来思考，既然工程代码没有编码问题、IDE缓存也没有问题，那使用mvn refresh为什么要抛出`Malformed \uxxxx`异常呢？是否是加载其他二方包依赖的时候，解析二方包的文件导致的？

带着这个问题，尝试google了下错误的内容，果然在stackflow中找到了解决方案，基本确定是maven解析repo依赖产生了问题

# 问题原因
使用 `mvn compile -e`查看具体的堆栈，发现maven在解析的时候有问题：

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/7a0d93ee_c4ed09dd.png)

借用IDEA自带的maven debug功能，进入`java.util.Properties`开始debug

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/f866f3f1_0e220e30.png)

发现确实有的依赖是乱码：

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/c8d7adad_db686eae.png)

往上找堆栈，发现下面这个文件确实有问题：

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/0bfcdf39_005cedd1.png)

打开文件一看，果然有下面的乱码：  
![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/13d2a10b_9c90a981.png)

将这个文件删除就好了。

然后重新import后，这个文件会重新生成：  
![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/5da8029e_88a7ecd2.png)

发现已经没有这些乱码了。受到影响的项目也可以顺利build了，完结撒花。

# 问题思考
1. 大部分遇到的问题，Google和GPT都能处理。举一反三，内部中间件问题搜索下语雀和ATA可能也会有意想不到的收获。
2. 印象中大学时候应该遇到过这个问题，当时只是简单的删除了repo重新refresh就OK了，没有深入排查。同时，更加深刻地理解了好记性不如烂笔头，遇到问题还是到记录一下。
3. resolver-status.properties的作用是什么？为什么删除resolver-status.properties就OK了？LLM答案如下：

> <font style="color:rgba(0, 0, 0, 0.88);">resolver-status.properties文件是Maven依赖解析器的元数据文件，主要用于</font>**<font style="color:rgba(0, 0, 0, 0.88);">跟踪依赖解析状态、缓存解析结果、记录仓库来源并优化构建性能</font>**<font style="color:rgba(0, 0, 0, 0.88);">。</font>
>

> <font style="color:rgba(0, 0, 0, 0.88);">文件中出现\u0000（null字符）表示文件损坏，可能由</font>**<font style="color:rgba(0, 0, 0, 0.88);">构建中断、磁盘空间不足、并发访问冲突或文件系统问题导致</font>**<font style="color:rgba(0, 0, 0, 0.88);">。重新生成的文件正常是因为Maven会根据当前依赖信息重新创建正确的元数据，不包含损坏数据，这种自我修复机制确保了构建的健壮性。</font>
>

4. 如何避免避免mvn构建过程中的resolver-status.properties问题？如果系统都正常的话，可能是并发构建导致，此时可以在IDE中设置如下参数，保证构建线程数为1，亲测对于中型工程来说，构建速度并没有减少太多

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/c0625668_fba539ac.png)

5. 之前没用过IDEA对MVN的构建过程进行debug，这次正好尝试一下，后面涉及到MVN命令的异常，又多了一种解决途径。

# 参考
[https://stackoverflow.com/questions/17043037/ant-malformed-uxxxx-encoding-in-propertyfile-task](https://stackoverflow.com/questions/17043037/ant-malformed-uxxxx-encoding-in-propertyfile-task)

