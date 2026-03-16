---
title: "Spring高效开发"
date: 2021-04-04 14:26
tags:
   - Java
   - Spring
categories:
   - 场景实践
description: "聚焦Spring IOC与AOP高效使用技巧，讲解Bean生命周期、扩展接口及优雅路由、策略模式等实战场景，附日志、异常、参数校验切面方案。"
---

不知道身为读者的你是否用过Java？也不知道使用Java的你是否使用过Spring？

如果上面两个问题你都回复是的话，那么这篇文章你应该好好看看，它可能会使你的工程代码更加丝滑。如果上面两个问题你给出任意一个否定的回答时，你可以离开，但是如果你执意驻留在此的话，你也可能会有一些不同的收获。

同时，**本文不会去讲Spring的源码和原理，只讨论如何高效使用**

### Spring的特征

如果你是Java开发者，当你看到这个标题的时候可能会嗤之以鼻：“Spring的特征，这能有什么？不就是IOC和AOP吗？”你想的没错，这确实是我本文要表达的内容。

如果我进一步提问，Spring的IOC和AOP该如何使用呢？这时候，你可能会略加思考，拿出你常用的`@Service`，`@Controller`，`@Component`和`@Autowired`等一些注解，并说出它们的特征和使用场景：“前三个注解将实例对象作为bean存储在Spring中，`@Autowired`注解通过控制反转的方式在我们使用的时候拿出来。通过IOC，我们不必关心对象的创建和其生命周期，也不必担心多个相同实例而浪费堆内存的空间。”而对于Spring的AOP来说，你可能会说它就是面向切面编程，AOP使得我们可以通过 *前置通知，后置通知，最终通知，异常通知，环绕通知* 的方式在特定场景中抽象出具体的逻辑，把代码聚焦在不同的业务领域，从而将更多精力放在业务逻辑上。

你讲的很对，但是可能还不够。

### IOC的使用

想要了解IOC的使用方式，我们就必须知道Spring实现IOC的方式其实就是通过一个map容器，Spring在初始化的时候会将扫描到的bean注射到容器中统一管理，在使用者调用的时候再从容器中取出这些bean。而我们对IOC的使用，其实就是对map容器的使用，对bean生命周期的使用。

#### 1. Bean的初始化

此时，我们发现，要想充分利用Spring的IOC，我们就需要充分了解到Spring中bean的生命周期（面试官偶尔会问到，但是大家都说那是八股文，我个人觉得这不是八股文，因为当你真正用到的时候，你就会无意识的记住了）

下面的生命周期是我参考`BeanFactory`的javadoc：

> 注意，bean在初始化之前还包括从配置文件中加载为`BeanDefination`，合并，然后再实例化为`BeanWrapper`，之后才是本文提的初始化

bean的初始化顺序：

1. 通过检查Aware接口并设置相关依赖来设置bean的属性

   > 通过`ApplicationContextAwareProcessor`实现

   * `BeanNameAware#setBeanName`
   * `BeanClassLoaderAware#setBeanClassLoader`
   * `BeanFactoryAware#setBeanFactory`
   * `EnvironmentAware#setEnvironment`

   * `EmbeddedValueResolverAware#setEmbeddedValueResolver`

   * `ResourceLoaderAware#setResourceLoader` （仅在在应用程序上下文中运行时适用）

   * `ApplicationEventPublisherAware#setApplicationEventPublisher` （仅适用于在应用程序上下文中运行的情况）

   * `MessageSourceAware#setMessageSource` （仅适用于在应用程序上下文中运行的情况）

   * `ApplicationContextAware#setApplicationContext`（仅适用于在应用程序上下文中运行的情况）

   * `ServletContextAware#setServletContext` （仅适用于在Web应用程序上下文中运行的情况）

2. 执行所有Bean初始化的前置处理

   * `BeanPostProcessor#postProcessBeforeInitialization`

     *@Autowired通过该方式实现*

3. 属性设置完成的处理

   * `InitializingBean#afterPropertiesSet`
   * a custom init-method definition（在xml中配置）

4. 执行Bean初始化的后置处理

   * `BeanPostProcessor#postProcessAfterInitialization`
   
     *aop通过它实现*

销毁bean：

1. 针对所有Bean销毁前的处理

   * `DestructionAwareBeanPostProcessors#postProcessBeforeDestruction`

     *` ApplicationListenerDetector`通过该方式实现*

2. Bean销毁时的处理

   * `DisposableBean#destroy`
   * a custom destroy-method definition（在xml中配置）

**在bean的生命周期中，我们可以通过Spring提供给我们的自定义接口和钩子来增强各个bean之间的联系，丰富特定bean的功能，从而达到我们的业务目的**。而这，就是SpringIOC提供给我们的重要的功能之一

对于`BeanPostProcessor`这个牛逼接口来说，它会在工厂初始化的时候，检查所有未实例化的bean，如果实现了该接口，则加入缓存。同时，它也有其他实现，有的实现会用于bean的实例化而不是初始化

#### 2. 其他扩展接口

但是，我们知道，对Bean之间的关系和能力的增强只满足了我们大部分业务需求，但是，我们并不能决定Bean在初始化之前和初始化之后的事情，为了解决这个问题，Spring给我们提供了`BeanFactoryPostProcessor`接口，该类的主要方法是：

1. 一个是`BeanFactoryPostProcessor#postProcessBeanFactory`，它发生在Bean初始化之前，主要用于与`BeanDefinition`和`BeanFactory`进行交互并对其进行修改


其实，除了这些扩展方式外，Spring还留给了我们其他的扩展方式，但是这些扩展方式太过偏僻（如主要用于bean实例化时的`BeanPostProcessor`的一些实现类。**Spring在bean的整个加载到使用的过程都对bean和beanFactory提供了扩展接口，你甚至可以通过这些接口在运行时自定义一个bean或者在运行时对一个bean的配置进行修改，或者你可以停止一个bean的实例和初始化等等**），是用于处理特殊的情况，跟本文的高效Spring开发主题不匹配，暂且不表。

这篇博客当需要的时候可以翻翻：[Spring的扩展文档](https://blog.csdn.net/woshilijiuyi/article/details/85396492)

#### 3. IOC场景实践

##### * 优雅路由

方法1：

> 我们可以实现`InitializingBean`接口，在该初始化到该bean将其以kv的形式放到某个工厂的map中，然后当request过来之后，可以通过request携带的k将该请求路由到我们固定的bean中去处理

```java
@Component
public class ARouter implements InitializingBean, Router {

    @Override
    public void afterPropertiesSet() throws Exception {
        // 注册该路由
        super.MAP.put("1",this);
    }
    @Override
    public void route() {
        // doSomething
    }
}
@RestController()
public class TestController {

    @PostMapping("/test")
    public TestDomain test(@RequestBody TestDomain testDomain) {
        // 使用该路由
        TestA.MAP.get(testDomain.getRouteId()).route();
        return testDomain;
    }
}
```

方法2：

> 利用Spring对map自动注册的原理，不过这里的key不能自定义，只能是该实例的类名

```java
@Component
public class ARouter implements Router {
    @Override
    public void route() {
        // doSomething
    }
}
@Component
public class Factory {
    @Autowired
    private Map<String, Router> routerMap;
    
    public getRouter(String key) {
        return routerMap.get(key);
    }
}
```

##### * 策略模式

其实策略模式也是优雅路由的一个延伸，因为找到不同的策略实现类就是通过路由完成的

##### * 特征发现

我们可以实现`BeanPostProcessor`接口，然后在bean初始化时发现该bean的某些特征，如该bean是否是某个类的子类，是否包括某注解，然后对该bean做进一步处理

```java
@Component
public class Test implements BeanPostProcessor {

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        if (bean.getClass().isAnnotationPresent(RestController.class)) {
            // 相应处理
        }
        return bean;
    }
}
```

##### * 获得Bean

我们可以通过各种织如接口来完成和Spring上下文的交互，譬如获得容器中的Bean

```java
@Component
public class Bean implements ApplicationContextAware {
    private ApplicationContext applicationContext;
 
    @Override
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        this.applicationContext = applicationContext;
    }
 
    public void doSomething() {
        Object bean = applicationContext.getBean(beanName);
    }
}
```

##### * 监听者模式

我们可以通过`ApplicationEventPubulisher`来实现事件的发布和监听

```java
@Component
public class DiyEventListener implements ApplicationListener<DiyEventListener.DiyEvent> {

    @Override
    public void onApplicationEvent(DiyEvent event) {
        System.out.println(event + "触发成功");
    }

    static class DiyEvent extends ApplicationEvent {

        public DiyEvent(Object source) {
            super(source);
        }
    }
}
@Component
public class Test implements ApplicationEventPublisherAware {

    private ApplicationEventPublisher applicationEventPublisher;

    @Override
    public void setApplicationEventPublisher(ApplicationEventPublisher applicationEventPublisher) {
        this.applicationEventPublisher = applicationEventPublisher;
    }

    public void doSomething() {
        applicationEventPublisher.publishEvent(new DiyEventListener.DiyEvent(1));
    }
}
```

### AOP的使用

通过上面的表述，我们知道，Spring的AOP特性是在bean初始化完成之后，通过`BeanFactoryPostProcessor`来完成的，那么通过AOP这样的切面编程特性我们可以做些什么呢？

其实我们会发现，**SpringIOC只能让我们在bean每次初始化或者销毁的前后做些事情，但是却解决不了实例在每次调用前后的功能拓展，而这，就是SpringAOP的作用**

#### 1. Spring对AOP的利用

Spring中对事务的处理默认是通过AOP来完成的。譬如事务的commit，rollback等等操作，都可以以切面的形式让程序帮我们完成

#### 2. AOP场景实践

##### * 统一日志处理

日志处理比较自定义话，这里看自己需求适当拦截

```java
@Component
@Aspect
public class SysLogAspect {

    /**
     * 后置通知
     */
    @After("execution(* cn.wxxlamp.blog.controller.*.*(..))")
    public void doAfter(){
        Log.log();
    }
}
```



##### * 统一异常拦截

将异常作为响应反馈给前端，防止后台宕机

```java
@Aspect
@Component
public class ExceptionAspect {

    /**
     * service 层切点
     */
    @Pointcut("execution(* cn.wxxlamp.demo.service.impl..*.*(..))")
    public void servicePointcut() {
    }

    @Around(value = "servicePointcut()")
    public Object ParamCheckAround(ProceedingJoinPoint joinPoint) throws Throwable {
        try{
            joinPoint.process();
        } catch(Exception.class) {
            // 自定义处理
            return DiyResponse.create();
        }
    }
}
```

当然，这里必须说明的是，这种AOP的统一异常拦截是在没有SpringMVC情况下的处理方案，如果用的SpringMVC，它提供了内置支持，处理异常直接用`ExceptionAdvice`这个注解即可。本方案只适合RPC调用时的情况

##### * 统一参数校验

我们可以对某些类的参数进行统一的校验

```java
@Target({ ElementType.METHOD, ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
public @interface ParamsCheck {
    boolean ignore() default false;
}

@Aspect
@Component
public class ValidateAspect {

    /**
     * service 层切点
     */
    @Pointcut("execution(* cn.wxxlamp.demo.service.impl..*.*(..))")
    public void servicePointcut() {
    }

    @Before(value = "servicePointcut()")
    public void ParamCheckAround(JoinPoint joinPoint) throws Throwable {
        // 判断是否需要校验
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        Method method = signature.getMethod();
        ParamsCheck paramsCheckAnnotation = method.getAnnotation(ParamsCheck.class);
        if (paramsCheckAnnotation != null && paramsCheckAnnotation.ignore()) {
            return joinPoint.proceed();
        }
        Object[] objects = joinPoint.getArgs();
        for (Object arg : objects) {
            if (arg == null) {
                break;
            }
           // 校验参数，失败抛出异常
        }
    }
}
```

### 后记

因为IOC和AOP，Spring得以在Java领域独占一方，引得无数开发者膜拜，几乎所有Java新手都会把学习Spring作为学习Java的一个阶段。对于我这样的新手来说，Spring是我日常使用的框架，它也是我学习Java的一个新台阶。但是，每当我在简历上写着“**了解Spring框架原理，熟悉Spring框架的使用**”的时候，我总是会有些汗颜。我相信，许多Java开发者一定和我一样，这便是这篇文章诞生的目的。

而且，通过对Spring的了解后，我发现Spring的全家桶很多都是基于Spring的扩展接口进行增加，不得不感叹Spring对开闭原则的贯彻和落实。尤其是很多扩展机制都是通过`BeanPostProcessor`和`BeanFactoryPostProcessor`这两个接口实现的。Spring通过`AbstractApplicationContext#refresh`把bean的加载编排为一个完备的流程，然后**定制各种时机和范围**的Bean处理器来对Bean实现扩展，实在是太屌了。

当然，虽然接触Spring一年有余，可是我还是个新手，这篇文章一定存在一些纰漏和未提及的要点，如果你有发现，请留言转达！

关于Spring的学习，我推荐这个[课程](https://mylearn.vmware.com/mgrReg/courses.cfm?ui=www_edu&a=one&id_subject=94106)

