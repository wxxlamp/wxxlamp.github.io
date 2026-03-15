---
title: "C和Java的区别"
tags:
   - Java
   - C++
categories:
   - 基础夯实
date: 2020-10-10 10:36
---

我是18年3月接触Java的，然后到现在差不多有一年半了，对Java有着一定的理解，最近在学习C++，所以准备列出来比较一下

<!--more-->

### 编译阶段

C++会先compiler，然后link。对于C++的编译来说，它会把.cpp转换为.obj文件，如果我们把.obj通过工具打开后可以发现，它其实就是汇编。.cpp中的#include, #define, #ifdef #ifend 是完全的复制粘贴。当我们在a.cpp中声明了一个没有实现的方法时，编译是不会报错 的。linker在连接的时候会报错，因为它找不到对应的实现

C++的link会判断是否有入口点，即main函数。同时也会连接每个文件。所以在这里有一个常见的错误，即是连接多个同样的声明。如果我们要防止同样的多个声明，就需要在实现上加上static（static使得其成为局部对外不可见的），或者使用inline，它会把当时的函数替换成函数体的内容

Java通过编译器直接生成所有的class文件，Java没有link，是通过package来进行约束每个class文件之间的关系



### 数据类型

C++： bool一个字节，char一个字节，int 4个字节，long4/8个字节，long long 8个字节，float 4个字节，double8个字节

java: bool 未知，byte 1个字节，char 2个字节，int 4个字节，short 2个字节，long 8个字节，float 4个，double 8个