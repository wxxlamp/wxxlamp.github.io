---
title: "SpringMVC源码分析"
tags:
   - Java
   - SpringMVC
   - Spring
categories:
   - 源码剖析
date: 2021-02-17 22:44
description: "本文系统解析SpringMVC的核心架构与工作原理，涵盖主要模块、执行流程、启动流程与初始化流程四个维度。详细介绍DispatcherServlet、HandlerMapping、HandlerAdapter、HandlerExecutionChain、HandlerMethodArgumentResolver等关键组件的职责与协作关系，并追踪从HTTP请求进入Tomcat到最终响应渲染的完整调用链。同时分析SpringMVC大量运用的工厂模式、策略模式、责任链模式等设计思想，并与Tomcat过滤器链设计进行对比，附源码片段辅助理解。"
---

前几天看了分析了@RequestBody的原理，并且DIY了一个参数解析器，今天趁热打铁，分析下SpringMVC的原理，主要包括启动流程和执行流程以及其设计思路。

SpringMVC中的MVC指的是model view 和 controller，view指的是渲染的视图，model指的是应用中包含的各种数据，controller则是负责业务处理的控制器。对于整个流程来说，当一个HTTP请求进入服务器之后，**controller**会对后台的数据，即**model**进行加工处理，然后由SpringMVC将这些**model**渲染为对应的**view**，形成response响应给client

### 主要模块

SpringMVC中有几个非常重要的类，分别是 `DispatherServlet`，`HandlerMapping`，`HandlerMethod`，`HandlerAdapter`，`HandlerExceptionResolver`，`HandlerInterceptor`，`HandlerExecutionChain`，`HandlerMethodArgumentResolver`和`HandlerMethodReturnValueHanlder`

1. `DispatherServlet`负责两件事情，一个是兼容Servlet规范（实现servlet的init方法，使得MVC相关的处理器在此时初始化）；一个是使得该MVC程序可以简单实用Spring的IOC（可以获得Environment，设置Environment和ApplicationContext）。除此之外，`DispatherServlet`还负责路由之后的核心逻辑的处理
2. 对于`HandlerMapping`来说，它负责将request和handlerExecutionChain关联起来，用于请求的路由处理。它的一个实现类R`equestMappingHandlerMapping`需要在初始化的时候检测@Controller注解或者@RequestMapping注解的类，将对应`RequestMappingInfo`（里面装着url的映射）和`HandlerMethod`关联起来
3. `HandlerMethod`封装了对应的`Method`和持有它的bean
4. `HandlerAdapter`依赖并代理了`HandlerMethod`，聚合了`ModelAndViewResolver`, `HandlerMethodArgumentResolver`和`HandlerMethodReturnValueHanlder`，用于处理参数，返回值和渲染视图
5. `HandlerExecutionChain`封装了`HandlerAdapter`和拦截器集合，通过它可以拿到`HandlerAdapter`，并且可以进行拦截器前置方法，后置方法和完成方法的监听和处理
6. `HandlerMethodArgumentResolver`和`HandlerMethodReturnValueHanlder`用户参数和返回值的个性化处理。用到的设计思想和HandlerAdapter是一样的
7. 最后一步，就是要去将数据渲染为对应的视图，而这一步就是由`ModelAndView`，`View`来完成的，它负责将model以不同的方式，如Jsp，Html等渲染成view，装入response中
8. 而几乎所有的框架都会有异常处理模块，SpringMVC也不例外，`HandlerExceptionResolver`则是负责这么一个处理流程的。它主要的功能就是将异常转换为合适的`ModelAndView`之后渲染到response中，而不至于出现5**的响应。其中，我们可以自定义发生异常后的响应方式。

对于这几个模块，我们可以这么理解：

> 对于一个普通的MVC设计思路来说，路由request和method是必不可少的，然后通过代理method的adapter来实现对参数和返回值的处理，又因为需要进行拦截器的拦截，所以需要一个interceptorChain和interceptor。最后，因为业务需要对某些异常进行特定的处理，所以我们还需要一个异常处理模块。

这，便是SpringMVC的核心类和模块。

### 执行流程

我们知道，对于Http请求来说，tomcat执行了`HttpServlet#service`方法，继承了`HttPServlet`的`FrameServlet`则是执行doService方法，而SpringMVC的`DispatcherServlet`则是继承了`HttpServlet`，进入到SpringMVC的流程中，在`DispatcherServlet`中的流程如下：

先通过`HandlerMapping`拿到request对应的`HandlerExecutionChain`，然后再拿到`HandlerExecutionChain中handler`对应的`HandlerAdapter`，执行`HandlerExecutionChain`中`interceptor#prehandle`方法。

再通过`handlerAdapter`去执行handler，handler其实对应的是之前注册的`HandlerMethod`（handlerMethod里面封装的映射的真正方法 *handler还有可能是原生的Servlet*），所以要执行handler.invoke，不过在这之前要去判断参数，这一步需要参数解析器`HandlerMethodArgumentResolver`。反射调用完之后，需要调用返回值解析器`HandlerMethodReturnValueHanlder`

真正方法执行完了之后，再执行`HandlerExecutionChain中interceptor#posthandle`方法进行拦截器的后置处理。

SpringMVC执行完之后返回的是`ModelAndView`，我们还需要对`ModelAndView`进行render，即把modelAndView中的view渲染到response中

当发生异常时，会将异常拉到用户业务自己的异常处理方法中，这时也需要对参数和返回值进行custom，此时就需要用到`HandlerExceptionResolver`系列了。因为用户标记的`@ExceptionHandler`方法已经被`ExceptionHandlerMethodResolver`找到并且注册（key为对应异常，value为对应方法），只需要调用该方法就可以对异常进行处理，此时的方法调用和之前的handler几乎没有区别

```java
// DispatherServlet#doDispath关于异常处理的部分源码
protected void doDispatch(HttpServletRequest request, HttpServletResponse response) throws Exception {
    ...
    try {
        ...
        try {  
            ...  
        }
        catch (Exception ex) {
            dispatchException = ex;
        }
        catch (Throwable err) {
            // As of 4.3, we're processing Errors thrown from handler methods as well,
            // making them available for @ExceptionHandler methods and other scenarios.
            dispatchException = new NestedServletException("Handler dispatch failed", err);
        }
        // 处理异常和渲染modelAndView的方法
        processDispatchResult(processedRequest, response, mappedHandler, mv, dispatchException);
    }
    ...
}
private void processDispatchResult(HttpServletRequest request, HttpServletResponse response,
			@Nullable HandlerExecutionChain mappedHandler, @Nullable ModelAndView mv,
			@Nullable Exception exception) throws Exception {

    boolean errorView = false;

    if (exception != null) {
        if (exception instanceof ModelAndViewDefiningException) {
            logger.debug("ModelAndViewDefiningException encountered", exception);
            mv = ((ModelAndViewDefiningException) exception).getModelAndView();
        }
        else {
            Object handler = (mappedHandler != null ? mappedHandler.getHandler() : null);
            // 真正处理异常的方法
            mv = processHandlerException(request, response, handler, exception);
            errorView = (mv != null);
        }
    }
    ...
}
```



### 启动流程

> 默认使用SpringBoot的自动装备

当我们点击SpringBoot的run之后，马老师，发绳肾么事了？

在回答问题之前，我们需要明白一件事情：SpringMVC在启动的时候需要利用SpringIOC的特性，同时也需要符合Servlet规范，即对servlet进行初始化。

SpringBoot会首先获得`AnnotationConfigServletWebServerApplicationContext`，然后进入到它的父类`AbstractApplicationContext#finishBeanFactoryInitialization`中，它会去遍历所有bean，对bean进行后置方法的处理。因为`RequestMappingHandlerMapping`需要对bean进行后置化处理，在这个过程中，它会去查找到有`@Controller`注解或者`@RequestMapping`注解的类，将对应`RequestMappingInfo`（里面装着url的映射）和`HandlerMethod`关联起来，在这个过程中，它不仅会注册用户自己标记的Controller，SpringMVC还内置了error的默认处理类`BasicErrorController`。

```java
// 附：AbstractHandlerMethodMapping.java 部分源码

/**
 * Detects handler methods at initialization.
 */
@Override
public void afterPropertiesSet() {
   initHandlerMethods();
}

/**
 * Scan beans in the ApplicationContext, detect and register handler methods.
 */
protected void initHandlerMethods() {
   
   ... 
       
   for (String beanName : beanNames) {
      if (!beanName.startsWith(SCOPED_TARGET_NAME_PREFIX)) {
         Class<?> beanType = null;
         try {
            beanType = obtainApplicationContext().getType(beanName);
         }
         catch (Throwable ex) {
            // An unresolvable bean type, probably from a lazy bean - let's ignore it.
            if (logger.isDebugEnabled()) {
               logger.debug("Could not resolve target class for bean with name '" + beanName + "'", ex);
            }
         }
         // 如果该bean有@Controller或者@RequestMapping注解，则获取它的方法
         if (beanType != null && isHandler(beanType)) {
            detectHandlerMethods(beanName);
         }
      }
   }
   // 后置处理，由子类实现，目前为空
   handlerMethodsInitialized(getHandlerMethods());
}
/**
  * Look for handler methods in a handler.
  * @param handler the bean name of a handler or a handler instance
  */
protected void detectHandlerMethods(final Object handler) {
    Class<?> handlerType = (handler instanceof String ?
			obtainApplicationContext().getType((String) handler) : handler.getClass());

	if (handlerType != null) {
		final Class<?> userType = ClassUtils.getUserClass(handlerType);
        // 将该类中的method和对应的RequestMappingInfo装入map中
        Map<Method, T> methods = MethodIntrospector.selectMethods(userType,
				(MethodIntrospector.MetadataLookup<T>) method -> {
                    try {
						return getMappingForMethod(method, userType);
					}
					catch (Throwable ex) {
						throw new IllegalStateException("Invalid mapping on handler class [" +
								userType.getName() + "]: " + method, ex);
                    }
				});
		if (logger.isDebugEnabled()) {
			logger.debug(methods.size() + " request handler methods found on " + userType + ": " + methods);
		}
		methods.forEach((method, mapping) -> {
			Method invocableMethod = AopUtils.selectInvocableMethod(method, userType);
            // 形成HandlerMethod类，并将该类与mapping进行映射
			registerHandlerMethod(handler, invocableMethod, mapping);
		});
	}
}
```

我们知道，Servlet需要通过init方法进行初始化，Servlet也需要在init方法中初始化。

当`AbstractApplicationContext#finishBeanFactoryInitialization`执行之后，便会执行`AbstractApplicationContext#finishRefresh`，在这个过程中，它会去启动Tomcat服务器，在Tomcat启动的过程中，调用`StandardWrapper#loadServlet`，而此时，则会对DefaultServlet进行初始化，对默认Servlet进行一些属性的设置

### 初始化流程

在服务启动之后，当一个request进入我们的服务器的时候，经过一系列的Valve和Filter后，会进入`StandardWrapper#allocate`中申请Servlet，同时对DispatherServlet进行初始化，它主要执行了`DispatherServlet#initStrategies`，然后在初始化策略的过程中会初始化`HandlerMapping`，`HandlerAdapter`，`HandlerExceptionResolver`，`ViewResolver`等等。在这个过程中，如果有对应的bean则获取，如果没有则拿到dispatcherServlet.properties中的默认策略

### 设计思路

1. SpringMVC中大量使用工厂模式，组合模式，策略模式和过滤器链模式等等，包括且不限于异常处理模块，参数解析和返回值渲染模块，方法代理模块（这个模块还用了代理模式）等等，它常见的表现形式如下：

   ```java
   interface Handler{
       public boolean supports(Object obj);
       public Object resolve(Object obj);
   }
   class Composite implements Handler{
       List<Handler> handlerList;
       
       @Override
      	public boolean supports(Object obj){
           for(Handler handler: handlerList) {
               if(handler.supports(obj)) {
                   return true;
               }
           }
           return false;
       }
       @Override
       public Object resolve(Object obj){
            for(Handler handler: handlerList) {
               if(handler.supports(obj)) {
                   return handler.resolve(obj);
               }
           }
       }
   }
   class DiyHandler implements Handler{
       ...
   }
   ```

2. 在责任链模式的使用过程中，我发现SpringMVC的过滤器链和Tomcat的还有一些不同，Tomcat的过滤器模式比较正统，而对于SpringMVC的责任链中，它其实只是起了一个拦截器的作用，只用到了两个类就实现了，即`HandlerInterceptor`和`HandlerExecutionChain`，前者有多个实现类，对应着多个不同种类的拦截器。而Tomcat当中，有两种方式实现了责任链模式，一个是pipeline/valve（valve的多个实现类对应着不同的水阀），另一个是filterChain/filter/filterConfig（chain负责调度多个filter并执行，filterConfig聚合了filter及其配置）
3. 同时，大量的Map形式或者类形式(如Match类)的缓存也是必须的

### 采坑点

1. 看SpringMVC最好不要直接用SpringBoot来看，它有自动装配，会让人看源码看的更加复杂
2. <---- 参数和返回值  **依赖关系**  和 <—<> 属性   **聚合关系**
4. Spring的BeanFactory和ApplicationContext，ApplicationListener，Environment和这四个对应的Aware接口
4. spring-web和spring-webmvc的依赖的区别，前者是将spring应用的web环境中，后者是实现web中的spring模式
5. 目前狭义上的SpringMVC是由服务端来负责渲染。从狭义上说，目前被大家广泛接受的前后端分离的形式，即后台只给前端传递json数据，这样是不属于MVC模式的，因为我们是直接把model转化为json传递给前端，由前端渲染。从源码中我们也可以看到，SpringMVC如果返回json数据的时候，返回的ModelAndView类是空的。所以我就产生了这样一个念头，简化SpringMVC

