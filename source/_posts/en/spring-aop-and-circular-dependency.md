---
title: >-
  Spring Initialization Failures with BeanPostProcessor and Circular
  Dependencies
date: 2021-07-31 18:36
tags:
  - Spring 框架
  - 问题排查
categories:
  - 采坑记录
description: >-
  Analyzes why manual AOP proxying by a BeanPostProcessor causes
  circular-dependency exceptions, traces Spring source code through the
  three-level cache mechanism, and offers native AOP and @Lazy solutions.
lang: en
translation_of: spring-aop-and-circular-dependency
---

*A secondary library in our team, TEST, intercepts beans by implementing `BeanPostProcessor` and manually creates AOP proxies during interception. In development, initialization fails when a proxied bean has a circular dependency, so I debugged it.*

This article covers the **Spring bean lifecycle, AOP, and circular dependencies**.

#### Prerequisites

1. First-level cache: `singletonObjects`, containing fully initialized objects.
2. Second-level cache: `earlySingletonObjects`, containing instantiated objects (used for circular dependencies).
3. Third-level cache: `singletonFactory`, containing other instantiation operations.

Spring obtains three forms of a bean instance:

1. `bean`: the original bean.
2. `exposedObject`: the extended bean.
3. `earlySingletonReference`: a bean obtained from the first two caches (and, when the parameter is true, the third cache); an early-exposed circular dependency.

**Assume class `a` is proxied, `a` references `b`, and `b` also references `a`. The source-code flow is as follows.**

#### Source-code analysis

> First obtain instance `a`.

1. `beanFactory.preInstantiateSingletons()` -> `AbstractBeanFactory#getBean` -> `AbstractBeanFactory#doGetBean`
   1. `DefaultSingletonBeanRegistry#getSingleton(String,true)`
      1. Nothing is stored in `singletonObjects`, and this bean is not being created, so this branch is not taken. ❌
   2. `AbstractBeanFactory#markBeanAsCreated` marks the bean as being created.
   3. `DefaultSingletonBeanRegistry#getSingleton(String, ObjectFactory<?>)`
      1. `AbstractAutowireCapableBeanFactory#createBean` creates the bean instance.
         1. `AbstractAutowireCapableBeanFactory#resolveBeforeInstantiation` performs work before bean instantiation (extensible: a user may create and return the object early). ❌
            1. `AbstractAutoProxyCreator#postProcessBeforeInstantiation` can create a proxy, but no proxy is created when annotations are used.
         2. `AbstractAutowireCapableBeanFactory#doCreateBean` enters the lambda from above and actually creates the bean.
            1. `AbstractAutowireCapableBeanFactory#createBeanInstance` instantiates the bean and wraps it in `BeanWrapper`.
            2. `DefaultSingletonBeanRegistry#addSingletonFactory(String beanName, ObjectFactory<?> singletonFactory)` adds a singleton factory, preparing the third-level cache for AOP (proxy creation) and circular dependencies.
            3. `AbstractAutowireCapableBeanFactory#populateBean` populates the bean instance.
               1. It performs post-processing after instantiation; if explicit instantiation is true, it returns immediately. ❌
               2. `AutowiredAnnotationBeanPostProcessor#postProcessProperties` injects fields annotated with `@Autowired`.
               3. It obtains dependency `b` (go to step 2).
               4. `AbstractAutowireCapableBeanFactory#initializeBean` initializes the bean and obtains the extended `exposedObject`; at this point there is no extension.
                  1. `AbstractAutowireCapableBeanFactory#applyBeanPostProcessorsBeforeInitialization` performs extension processing before initialization.
                  2. `AbstractAutowireCapableBeanFactory#applyBeanPostProcessorsAfterInitialization` performs extension processing after initialization.
                  3. With no extension, `bean==exposedObject`. **For TEST, `exposedObject=proxy` here, and its fields have not been populated.**
               5. `DefaultSingletonBeanRegistry#getSingleton(String,false)` reads an object from the first and second caches and assigns it to `earlySingletonReference`. At this point the second cache contains the instance, and it is a proxy. **Other implementations store the original bean.**
               6. Because `bean==exposedObject`, the proxy is returned directly. **For TEST, `bean!=exposedObject`; the system detects that another bean has already used this bean and throws an exception.**
   4. Put the bean into the first-level cache and remove it from the second-level cache.

> Obtain instance `b`.

2. `AbstractBeanFactory#getBean` -> `AbstractBeanFactory#doGetBean` obtains a field dependency.
   1. `DefaultSingletonBeanRegistry#getSingleton(String,true)`
      1. `singletonObjects` has no entry and the bean is not being created, so this branch is not taken. ❌
   2. `AbstractBeanFactory#markBeanAsCreated` marks the bean as being created.
   3. `DefaultSingletonBeanRegistry#getSingleton(String, ObjectFactory<?>)`
      1. `AbstractAutowireCapableBeanFactory#createBean` creates the bean instance.
         1. `AbstractAutowireCapableBeanFactory#resolveBeforeInstantiation` performs pre-instantiation work. ❌
            1. `AbstractAutoProxyCreator#postProcessBeforeInstantiation` can create a proxy, but annotations do not create one here.
         2. `AbstractAutowireCapableBeanFactory#doCreateBean` actually creates the bean.
            1. `AbstractAutowireCapableBeanFactory#createBeanInstance` instantiates and wraps the bean in `BeanWrapper`.
            2. `DefaultSingletonBeanRegistry#addSingletonFactory(String beanName, ObjectFactory<?> singletonFactory)` adds the singleton factory for AOP proxy creation and circular dependencies.
            3. `AbstractAutowireCapableBeanFactory#populateBean` populates the bean.
               1. The post-instantiation operation returns immediately when explicit instantiation is true. ❌
               2. `AutowiredAnnotationBeanPostProcessor#postProcessProperties` injects `@Autowired` fields.
               3. It gets dependency `a` (go to step 3) and receives the proxy bean. **Other implementations store the original bean.**
               4. `AbstractAutowireCapableBeanFactory#initializeBean` initializes the bean and gets `exposedObject`.
                  1. It applies post-processors before initialization.
                  2. It applies post-processors after initialization.
                  3. There is no extension, so `bean==exposedObject`.
               5. `DefaultSingletonBeanRegistry#getSingleton(String,false)` reads from the first and second caches. Both are empty, and entering the third cache is disallowed, so `earlySingletonReference` is empty.
               6. The bean instance is therefore returned directly.
   4. Put `b` into the first-level cache.

> Obtain instance `a`.

3. `AbstractBeanFactory#getBean` -> `AbstractBeanFactory#doGetBean` obtains the field dependency.
   1. `DefaultSingletonBeanRegistry#getSingleton(String)`
      1. `singletonObjects` has no entry, but the bean is already being created.
         1. `DefaultSingletonBeanRegistry#getSingleton(String,true)`
            1. Neither `singletonObjects` nor `earlySingletonObjects` has an entry, so Spring enters the third cache: `singletonFactory`.
            2. `AbstractAutowireCapableBeanFactory#getEarlyBeanReference` is the third-cache operation.
               1. `AbstractAutoProxyCreator#wrapIfNecessary` creates the proxy. **Other implementations do not take this step.**
               2. Store `(a, proxy)` in the second-level cache. **Other implementations store the original bean.**

#### Diagram

![Spring AOP circular dependency](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/85995399_spring-aop-and-circular-dependency.png)

### Cause

Suppose `a` is proxied, `a` references `b`, and `b` references `a`.

With normal AOP, when `b` is populated with `a`, `a` is already a proxy.

With TEST's approach, however, `a` is still the original bean when `b` is populated with it; it is proxied only afterward, so the reference cannot be used.

### Solutions

1. For the secondary library: use native AOP annotations.
2. On the consumer side: add `@Lazy` to the non-proxied bean in the circular dependency so it is not loaded during container refresh and is loaded only when used.

   With `@Lazy`, the path at 121233 is not taken; at 121235, `earlySingletonReference` is empty, and Spring directly returns the proxy class from `exposedObject`.

   When the circular-dependency field is actually referenced, it loads the earlier proxy bean and completes the circular dependency.
