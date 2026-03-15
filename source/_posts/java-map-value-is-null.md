---
title: "当Map的值为NULL"
tags:
   - Java
categories:
   - 采坑记录
date: 2022-07-31 10:36
description: "排查Java中Map值为NULL引发的诡异问题，揭示不同Map实现对null值处理的差异。"
---

最近在开发过程中遇到了一个非常令人费解的情况，排查了将近一早上还没找到头绪，还是在师兄的帮助下，才发现了问题。

### 问题复现

先看一段代码：
```java
// 调用远程RPC方法，获取map
Map<String, Object> map = remoteMethod.queryMap();
// 如果包含对应key，则进行业务处理
if(map.contains(KEY)) {
    String value = (String)map.get(KEY);
    System.out.println(value);
}
```
这段代码乍一看，逻辑没有什么问题，如果查询到的map包含这个key，就拿到这个key的值，并转为String类型，并打印这个value。
但是事实上，程序会偶发的打印出 `null` ，所以我就开始排查是否是因为`map.get(KEY) = null`，排查方式如下：
```json
// 调用远程RPC方法，获取map
Map<String, Object> map = remoteMethod.queryMap();
// 如果包含对应key，则进行业务处理
System.out.println(JSON.toJsonString(map));
```
结果对应的输出也只是一个非常简单的`{}`字符串，这个时候我就非常懵逼了，明明map中没有对应的key，为啥还会执行`map.contains(KEY)`的逻辑呢？

### 问题原因

最后，经过排查，发现了两个问题

1. `HashMap`的value可以为`null`，这就意味着虽然`hashMap.get(KEY) == null`，但是`hashMap.contains(KEY) == true`也是完全可以存在的。这就是第一段代码出现问题的原因
2. Fastjson和Gson默认不会打印value为null的键值对，即当`hashMap.get(KEY) == null && hash.contains(KEY)`时，常见的json框架如没有特殊制定的情况下，是不会将`{KEY:null}`打印出来的，这也是第二段代码没有排查出来问题的原因

结合这两个问题来看，原因就十分明显了，远程的RPC服务返回的Map中的value包含null值，导致仍然可以进入正常的业务逻辑中；同时，又因为没有json默认不会打印value=null的键值对，所以导致了问题排查的困难

### 解决方案

在开发过程中，尤其是调用外部接口或者从数据库获取数据的时候，由于Java是强类型，我们都喜欢把扩展字段的类型封装成`Map<String, Object>`，然后再根据具体的场景将value强转为不同的类型（如`String`），这个时候，无论是`#get`还是`#put`都需要相当注意：

1. `#put`方法在使用的时候，如果value=null，就尽量不要put进去
2. 在要对value处理的情况下，尽量不要使用`#contains`判断key的存在，要使用`(V = (map.get(KEY))) != null`会更好一点


### 感悟总结

`Map`实现类的区别，是面试很常见的一个问题，其中的一个不同点就是key=null和value=null的情况，但是在看书的时候只是匆匆略过，知道有这么一个事情，有点不以为意，只有真正踩坑的时候，才明白有多重要~

> HashMap: key和value均可以为null
> HashTable：key和value均不可以为null
> ConcurrentHashMap：key和value均不可以为null

其实，仔细想了一下，常见的json框架默认不打印`{KEY:null}`也是有原因的，因为如果很多json2Str方法的作用都是打印日志或者持久化到数据库中的，如果把大量的value=null打印出来，尤其是在数据库持久化的时候，会产生大量无用的数据，多少有点浪费的。不过跟资金相关的日志，建议还是把null值打印出来比较好，更方便排查问题了:)
