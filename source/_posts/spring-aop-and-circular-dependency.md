---
title: "BeanPostProcessor在循环依赖情况下导致的Spring初始化异常"
date: 2021-07-31 18:36
tags:
   - Java
   - Spring
   - Aop
categories:
   - 采坑记录
description: "本文针对一个真实生产问题展开深度分析：某二方库通过BeanPostProcessor对Bean进行手动AOP代理，当被代理的Bean存在循环依赖时会抛出初始化异常。作者结合Spring三级缓存机制（singletonObjects、earlySingletonObjects、singletonFactory），逐步追踪Bean创建的完整源码调用链，揭示问题根因——手动代理时机滞后导致二级缓存中存入的是原始Bean而非代理Bean，与后续exposedObject不一致进而触发异常。提供了使用原生AOP注解和@Lazy两种解决方案。"
---

*组里有一个二方库TEST，通过实现BeanPostProcessor来对bean进行拦截，同时，在拦截的过程中对bean进行手动的aop代理，但是在开发环境中，当被代理的bean被循环依赖时，会初始化异常，特此debug一下*

这篇文章会涉及到**springbean的生命周期，aop，循环依赖**

#### 先导知识

1. 一级缓存`singletonObjects`，初始化完成

2. 二级缓存`earlySingletonObjects`，实例化完成（用于循环依赖）
3. 三级缓存`singletonFactory`，其他实例化操作

Spring获得实例的三种bean：

1. bean：原始bean
2. exposedObject：扩展bean
3. earlySingletonReference：从前两个缓存中拿到的bean（如果参数为true则有第三个缓存），提前暴露的循环依赖

**假如说是类a被代理，同时a引用b，b也引用a，那么源码如下：**

#### 源码分析

> 首先获取实例a

1. `beanFactory.preInstantiateSingletons()` -> `AbstractBeanFactory#getBean` -> `AbstractBeanFactory#doGetBean`
   1. `DefaultSingletonBeanRegistry#getSingleton(String,true)` 
      1. `singletonObjects`这个缓存中没存，并且这个bean没有在创建中，所以不走这个分支 ❌
   2. `AbstractBeanFactory#markBeanAsCreated` 标记bean正在创建中
   3. `DefaultSingletonBeanRegistry#getSingleton(String, ObjectFactory<?>)`
      1. `AbstractAutowireCapableBeanFactory#createBean` 创建Bean实例
         1. `AbstractAutowireCapableBeanFactory#resolveBeforeInstantiation` bean实例化前操作，（可扩展，此时用户可以提前创建该对象，如果创建对象，则返回）❌
            1. `AbstractAutoProxyCreator#postProcessBeforeInstantiation`可以创建代理对象，但是用注解的时候没有创建代理对象
         2. `AbstractAutowireCapableBeanFactory#doCreateBean` 进入刚才函数式接口的表达式：真正创建bean
            1. `AbstractAutowireCapableBeanFactory#createBeanInstance` 实例化bean，此时用BeanWrapper包裹bean
            2. `DefaultSingletonBeanRegistry#addSingletonFactory(String beanName, ObjectFactory<?> singletonFactory)` 增加单例工厂，为aop（创建proxy）循环依赖做准备，三级缓存
            3. `AbstractAutowireCapableBeanFactory#populateBean` 填充bean实例
               1. 实例化Bean后置操作，如果显示实例化true，则直接返回 ❌
               2. `AutowiredAnnotationBeanPostProcessor#postProcessProperties` @autowired注解通过该方法对属性进行注入
               3. 获取到依赖的属性b（转2）
               4. `AbstractAutowireCapableBeanFactory#initializeBean` 初始化bean，获得扩展的exposedObject，此时没有扩展
                  1. `AbstractAutowireCapableBeanFactory#applyBeanPostProcessorsBeforeInitialization`初始化之前的扩展处理
                  2. `AbstractAutowireCapableBeanFactory#applyBeanPostProcessorsAfterInitialization`初始化之后的扩展处理
                  3. 没有扩展，所以bean==exposedObject / **对于TEST来说，此时exposedObject=proxy，且里面的参数没有被填充**
               5. `DefaultSingletonBeanRegistry#getSingleton(String,false)` 从一级缓存和二级缓存中获取对象赋值给`earlySingletonReference`。此时第二个缓存中有该实例，且存的是proxy / **其他的存的是原始bean** 
               6. 因为bean==exposeObject，所以直接把proxy返回 / **对于TEST来说，此时bean!=exposedObject，同时系统检测该bean已经被其他bean利用，所以抛出异常**
   4. 将该bean放入一级缓存，并将bean从二级缓存中删掉
> 获取实例b
2. `AbstractBeanFactory#getBean` -> `AbstractBeanFactory#doGetBean` 获取属性依赖
   1. `DefaultSingletonBeanRegistry#getSingleton(String,true)` 
      1. `singletonObjects`这个缓存中没存，并且这个bean没有在创建中，所以不走这个分支 ❌
   2. `AbstractBeanFactory#markBeanAsCreated` 标记bean正在创建中
   3. `DefaultSingletonBeanRegistry#getSingleton(String, ObjectFactory<?>)`
      1. `AbstractAutowireCapableBeanFactory#createBean` 创建Bean实例
         1. `AbstractAutowireCapableBeanFactory#resolveBeforeInstantiation` bean实例化前操作，（可扩展，此时用户可以提前创建该对象，如果创建对象，则返回）❌
            1. `AbstractAutoProxyCreator#postProcessBeforeInstantiation`可以创建代理对象，但是用注解的时候没有创建代理对象
         2. `AbstractAutowireCapableBeanFactory#doCreateBean` 进入刚才函数式接口的表达式：真正创建bean
            1. `AbstractAutowireCapableBeanFactory#createBeanInstance` 实例化bean，此时用BeanWrapper包裹bean
            2. `DefaultSingletonBeanRegistry#addSingletonFactory(String beanName, ObjectFactory<?> singletonFactory)` 增加单例工厂，为aop（创建proxy）循环依赖做准备，三级缓存
            3. `AbstractAutowireCapableBeanFactory#populateBean` 填充bean实例
               1. 实例化Bean后置操作，如果显示实例化true，则直接返回 ❌
               2. `AutowiredAnnotationBeanPostProcessor#postProcessProperties` @autowired注解通过该方法对属性进行注入
               3. 获取到依赖的属性a（转3），拿到代理bean / **其他的存的是原始bean**
               4. `AbstractAutowireCapableBeanFactory#initializeBean` 初始化bean，获得扩展的exposedObject
                  1. `AbstractAutowireCapableBeanFactory#applyBeanPostProcessorsBeforeInitialization`初始化之前的扩展处理
                  2. `AbstractAutowireCapableBeanFactory#applyBeanPostProcessorsAfterInitialization`初始化之后的扩展处理
                  3. 没有扩展，所以bean==exposeObject
               5. `DefaultSingletonBeanRegistry#getSingleton(String,false)` 从一级缓存和二级缓存中获取对象。此时两个缓存均没有，且不允许进入第三个缓存，所以`earlySingletonReference`为空
               6. 所以直接返回bean实例
   4. 将bean放入一级缓存
> 获取实例a
3. `AbstractBeanFactory#getBean` -> `AbstractBeanFactory#doGetBean` 获取属性依赖
   1. `DefaultSingletonBeanRegistry#getSingleton(String)` 
      1. `singletonObjects`这个缓存中没存，但是bean已经在创建中了
         1. `DefaultSingletonBeanRegistry#getSingleton(String,true)`
            1. `singletonObjects`和`earlySingletonObjects`这两个缓存中都没有，进入三级缓存：`singletonFactory`
            2. `AbstractAutowireCapableBeanFactory#getEarlyBeanReference` 这个就是三级缓存
               1. `AbstractAutoProxyCreator#wrapIfNecessary` 生成代理 / **其他的没有这一步**
               2. 存入二级缓存（a, proxy）/ **其他的存的是原始bean**

#### 图片

![SpringAOP循环依赖](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/85995399_spring-aop-and-circular-dependency.png)

### 问题原因

假如说是类a被代理，同时a引用b，b也引用a

对于正常的aop来说，会在b填充a的时候，a就已经是代理了

但是对于TEST的做法，它在b填充a的时候还是原来的bean，而在之后才代理，所以无法引用

### 解决方案

1. 二方包：采用原生aop注解

2. 用户侧：循环依赖的非代理bean，增加@lazy注解，不在容器刷新时加载，而是在使用时加载

   原因是增加lazy注解后，121233处不会经过，121235处`earlySingletonReference`为空，直接返回`exposedObject`的代理类

   当循环依赖属性真正被引用的时候，它会去加载之前的代理bean，完成循环依赖
