---
title: Practical Techniques for Productive Spring Development
date: 2021-04-04 14:26
tags:
  - Spring 框架
  - Java
  - 研发效能
categories:
  - 场景实践
description: >-
  Practical Spring IoC and AOP techniques: bean lifecycles, extension
  interfaces, routing, strategies, logging, exception handling, and parameter
  validation.
lang: en
translation_of: spring-user-guide
---

Have you used Java? And if so, have you used Spring?

If your answer to both is yes, this article deserves a look: it may help make your project code smoother. If either answer is no, you can move on—but if you stay, you may still discover something useful.

Also, **this article does not explain Spring's source code or internals; it focuses on using it effectively.**

### Spring's Features

As a Java developer, you might scoff at that heading: “What else is there to say about Spring's features? Aren't they just IoC and AOP?” You are right; that is exactly what I want to discuss.

But if I ask how to use Spring's IoC and AOP, you might pause, then bring up familiar annotations such as `@Service`, `@Controller`, `@Component`, and `@Autowired`, explaining their roles: “The first three store instances as beans in Spring, and `@Autowired` retrieves them when needed through inversion of control. IoC means we need not manage object creation or lifecycles, nor waste heap space on duplicate instances.” For AOP, you might explain aspect-oriented programming and how *before, after-returning, after-finally, after-throwing, and around advice* extract shared logic from particular scenarios, organize code around business domains, and let us concentrate on business logic.

That is correct, but it may not be enough.

### Using IoC

To understand how to use IoC, we should recognize that Spring implements it around a map-like container. During initialization, Spring places discovered beans into this container for centralized management and retrieves them when callers need them. Using IoC therefore means making use of this container and the bean lifecycle.

#### 1. Bean Initialization

To get the most from Spring IoC, we need to understand its bean lifecycle. Interviewers sometimes ask about this, and people dismiss it as rote interview trivia. I disagree: once you actually use it, you remember it naturally.

The following lifecycle is based on the `BeanFactory` Javadoc:

> Before initialization, beans are loaded from configuration into `BeanDefinition` objects, merged, and instantiated as `BeanWrapper` objects. Only then does the initialization described here begin.

Bean initialization order:

1. Set bean properties by checking Aware interfaces and supplying the relevant dependencies.

   > Implemented through `ApplicationContextAwareProcessor`.

   * `BeanNameAware#setBeanName`
   * `BeanClassLoaderAware#setBeanClassLoader`
   * `BeanFactoryAware#setBeanFactory`
   * `EnvironmentAware#setEnvironment`
   * `EmbeddedValueResolverAware#setEmbeddedValueResolver`
   * `ResourceLoaderAware#setResourceLoader` (only when running in an application context)
   * `ApplicationEventPublisherAware#setApplicationEventPublisher` (only when running in an application context)
   * `MessageSourceAware#setMessageSource` (only when running in an application context)
   * `ApplicationContextAware#setApplicationContext` (only when running in an application context)
   * `ServletContextAware#setServletContext` (only when running in a web application context)

2. Run preprocessing before bean initialization.

   * `BeanPostProcessor#postProcessBeforeInitialization`

     *These notes associate @Autowired processing with this mechanism.*

3. Handle completion of property setting.

   * `InitializingBean#afterPropertiesSet`
   * A custom init-method definition configured in XML.

4. Run postprocessing after bean initialization.

   * `BeanPostProcessor#postProcessAfterInitialization`

     *AOP is implemented through this mechanism.*

Bean destruction:

1. Run preprocessing before destroying beans.

   * `DestructionAwareBeanPostProcessors#postProcessBeforeDestruction`

     *`ApplicationListenerDetector` uses this mechanism.*

2. Perform bean destruction.

   * `DisposableBean#destroy`
   * A custom destroy-method definition configured in XML.

**Throughout a bean's lifecycle, Spring's extension interfaces and hooks let us strengthen relationships between beans and enrich individual beans to meet business needs.** This is one of Spring IoC's important capabilities.

For the powerful `BeanPostProcessor` interface, the factory checks beans that have not yet been instantiated during initialization and caches those implementing it. There are also other implementations, some used during bean instantiation rather than initialization.

#### 2. Other Extension Interfaces

Enhancing relationships and capabilities between beans meets most business needs, but does not give us control over everything before and after initialization. Spring provides `BeanFactoryPostProcessor` to address this. Its main method is:

1. `BeanFactoryPostProcessor#postProcessBeanFactory`, which runs before bean initialization and primarily interacts with and modifies `BeanDefinition` and `BeanFactory`.

Spring offers additional extension mechanisms, but some are more specialized—for example, certain `BeanPostProcessor` implementations primarily used during instantiation. **Spring provides extension interfaces for beans and BeanFactory throughout the entire journey from loading to use. You can even define a bean at runtime, change its configuration at runtime, or prevent its instantiation or initialization.** These mechanisms address special cases and fall outside this article's focus on productive everyday development.

This post is useful when needed: [Spring extension documentation (in Chinese)](https://blog.csdn.net/woshilijiuyi/article/details/85396492).

#### 3. Practical IoC Scenarios

##### * Elegant Routing

Approach 1:

> Implement `InitializingBean` and register the bean as a key-value pair in a factory's map during initialization. When a request arrives, use its key to route it to the corresponding bean.

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

Approach 2:

> Use Spring's automatic map injection. In this approach, the key cannot be customized directly; the notes describe it as the instance's class name.

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

##### * Strategy Pattern

The Strategy pattern is an extension of elegant routing: finding the appropriate strategy implementation is itself a routing operation.

##### * Feature Discovery

Implement `BeanPostProcessor` to discover characteristics during bean initialization, such as whether the bean is a subclass of a particular class or carries an annotation, then process it accordingly.

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

##### * Retrieving Beans

Various Aware interfaces let us interact with the Spring context, for example to retrieve a bean from the container.

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

##### * Listener Pattern

We can publish and listen for events through `ApplicationEventPublisher`.

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

### Using AOP

The discussion above shows that Spring's AOP capability is applied after bean initialization through postprocessing—the original notes refer to `BeanFactoryPostProcessor` here. What can aspect-oriented programming help us accomplish?

**Spring IoC lets us perform work around bean initialization and destruction, but does not by itself extend behavior around every method invocation. That is the role of Spring AOP.**

#### 1. How Spring Uses AOP

Spring's transaction handling uses AOP by default. Operations such as commit and rollback can be performed automatically through aspects.

#### 2. Practical AOP Scenarios

##### * Centralized Logging

Logging is highly application-specific, so intercept the calls appropriate to your needs.

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

##### * Centralized Exception Handling

Return exceptions to the frontend as responses to prevent backend failures.

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

This AOP approach to centralized exception handling applies when Spring MVC is absent. Spring MVC provides built-in support; the original notes call the relevant annotation `ExceptionAdvice`. The approach shown here is intended for RPC calls.

##### * Centralized Parameter Validation

We can validate parameters across selected classes in a consistent way.

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

### Afterword

IoC and AOP have given Spring a commanding place in the Java ecosystem and won over countless developers. Almost every Java beginner treats learning Spring as a stage in learning Java. For a beginner like me, Spring is both my everyday framework and another step in my Java education. Yet whenever I write **“understand Spring's internals and am familiar with using the framework”** on my résumé, I feel a little embarrassed. I believe many Java developers share that feeling, which is why I wrote this article.

As I learned more, I realized that much of the Spring ecosystem builds on Spring's extension interfaces. Its commitment to the Open/Closed Principle is impressive. Many extension mechanisms rely on `BeanPostProcessor` and `BeanFactoryPostProcessor`. Spring organizes bean loading into a complete flow through `AbstractApplicationContext#refresh`, then **customizes bean processors for different moments and scopes** to extend beans. That is seriously impressive.

Of course, although I have used Spring for over a year, I am still a beginner. This article surely contains omissions and mistakes. If you spot any, please leave a comment!

For learning Spring, I recommend this [course](https://mylearn.vmware.com/mgrReg/courses.cfm?ui=www_edu&a=one&id_subject=94106).

