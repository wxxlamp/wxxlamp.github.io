---
title: An Analysis of Spring MVC Internals
tags:
  - Spring 框架
  - Java
categories:
  - 源码剖析
date: 2021-02-17 22:44
description: >-
  A systematic explanation of Spring MVC's architecture and operation, covering
  its central components, request flow, startup and initialization, design
  patterns, and relevant source code.
lang: en
translation_of: spring-mvc-desc
---

A few days ago I analyzed how `@RequestBody` works and built a custom argument resolver. While the subject is still fresh, I will analyze Spring MVC itself: its startup flow, execution flow, and design ideas.

MVC stands for model, view, and controller. The view is the rendered presentation, the model contains application data, and the controller performs business processing. When an HTTP request enters the server, the **controller** processes backend data—the **model**—and Spring MVC renders that model as the corresponding **view**, forming a response for the client.

### Main Modules

Several Spring MVC classes are especially important: `DispatherServlet`, `HandlerMapping`, `HandlerMethod`, `HandlerAdapter`, `HandlerExceptionResolver`, `HandlerInterceptor`, `HandlerExecutionChain`, `HandlerMethodArgumentResolver`, and `HandlerMethodReturnValueHanlder`.

1. `DispatherServlet` has two responsibilities. It conforms to the Servlet specification by implementing the servlet `init` method and initializing MVC handlers there, and it lets an MVC program use Spring IoC conveniently by obtaining and setting `Environment` and `ApplicationContext`. It also handles the central logic after routing.
2. `HandlerMapping` associates a request with a `HandlerExecutionChain` and therefore handles routing. During initialization, its implementation `RequestMappingHandlerMapping` detects classes annotated with `@Controller` or `@RequestMapping`, then associates each `RequestMappingInfo`, which contains URL mappings, with a `HandlerMethod`.
3. `HandlerMethod` wraps a `Method` and the bean that owns it.
4. `HandlerAdapter` depends on and delegates to `HandlerMethod`. It aggregates `ModelAndViewResolver`, `HandlerMethodArgumentResolver`, and `HandlerMethodReturnValueHanlder` to process arguments, return values, and view rendering.
5. `HandlerExecutionChain` wraps a `HandlerAdapter` and a collection of interceptors. It provides the adapter and coordinates interceptor pre-processing, post-processing, and completion callbacks.
6. `HandlerMethodArgumentResolver` and `HandlerMethodReturnValueHanlder` customize arguments and return values. Their design follows the same idea as `HandlerAdapter`.
7. The final step renders data as a view. `ModelAndView` and `View` perform this work, rendering a model through JSP, HTML, or another representation and placing the result in the response.
8. Almost every framework needs exception handling, and Spring MVC is no exception. `HandlerExceptionResolver` converts an exception into an appropriate `ModelAndView` and renders it into the response instead of simply producing a 5xx response. Applications can customize the response to an exception.

These modules can be understood as follows:

> An ordinary MVC design must route requests to methods. An adapter around the method processes parameters and return values. Interception requires an interceptor chain and interceptors. Finally, because a business needs custom handling for certain failures, it also needs an exception-handling module.

These are Spring MVC's central classes and modules.

### Execution Flow

For an HTTP request, Tomcat executes `HttpServlet#service`. `FrameworkServlet`, which inherits `HttpServlet`, executes `doService`, and Spring MVC's `DispatcherServlet` continues the framework flow.

First, `HandlerMapping` obtains the request's `HandlerExecutionChain`. Spring then finds the `HandlerAdapter` corresponding to the handler in that chain and invokes each interceptor's `preHandle` method.

The adapter executes the handler, which normally corresponds to a previously registered `HandlerMethod` wrapping the actual mapped method, though a handler can also be a native servlet. Before calling `handler.invoke`, Spring resolves arguments through `HandlerMethodArgumentResolver`. After the reflective invocation, it processes the result through `HandlerMethodReturnValueHanlder`.

After the target method completes, Spring invokes the chain's interceptor `postHandle` methods.

Spring MVC returns a `ModelAndView`, which must then be rendered: its view is written into the response.

When an exception occurs, it is routed to the application's exception handler, whose parameters and return value also require customization through the `HandlerExceptionResolver` family. Methods marked with `@ExceptionHandler` have already been found and registered by `ExceptionHandlerMethodResolver`, mapping each exception to its method. Calling that method handles the exception, and the invocation is nearly identical to an ordinary handler call.

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



### Startup Flow

> This discussion assumes Spring Boot's default auto-configuration.

After clicking Spring Boot's Run button, what exactly happens?

Before answering, remember that Spring MVC startup must use Spring IoC while also conforming to the Servlet specification by initializing a servlet.

Spring Boot first obtains an `AnnotationConfigServletWebServerApplicationContext`, then enters its superclass method `AbstractApplicationContext#finishBeanFactoryInitialization`, which traverses every bean and performs post-processing. `RequestMappingHandlerMapping` participates in that processing. It finds classes annotated with `@Controller` or `@RequestMapping` and associates their `RequestMappingInfo`, containing URL mappings, with `HandlerMethod` objects. It registers both application controllers and Spring MVC's built-in default error handler, `BasicErrorController`.

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

Servlets are initialized through their `init` method, so the Spring MVC servlet must also initialize there.

After `AbstractApplicationContext#finishBeanFactoryInitialization`, Spring executes `AbstractApplicationContext#finishRefresh`. During this stage it starts Tomcat. Tomcat startup calls `StandardWrapper#loadServlet`, which initializes `DefaultServlet` and sets its default properties.

### Initialization Flow

After the service starts and a request enters the server, it passes through valves and filters before `StandardWrapper#allocate` allocates a servlet and initializes `DispatherServlet`. The servlet chiefly runs `DispatherServlet#initStrategies`, which initializes `HandlerMapping`, `HandlerAdapter`, `HandlerExceptionResolver`, `ViewResolver`, and related strategies. If corresponding beans exist, it uses them; otherwise it loads defaults from `dispatcherServlet.properties`.

### Design Ideas

1. Spring MVC makes extensive use of factory, composite, strategy, filter-chain, and other patterns. They appear in exception handling, argument resolution, return-value rendering, and method adapters, which also use the proxy pattern. A typical form is:

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

2. While examining chains of responsibility, I found that Spring MVC's chain differs from Tomcat's. Tomcat implements the conventional pattern, while Spring MVC's chain acts primarily as an interceptor and needs only `HandlerInterceptor` and `HandlerExecutionChain`. The former has multiple implementations representing different interceptors. Tomcat implements the pattern in two ways: pipeline/valve, whose valve implementations represent different valves, and filterChain/filter/filterConfig, where the chain schedules and executes filters while each filterConfig aggregates a filter and its configuration.
3. Numerous caches represented by maps or classes such as `Match` are also essential.

### Lessons Learned

1. When studying Spring MVC, avoid starting directly with Spring Boot. Auto-configuration makes source-code analysis more complicated.
2. `<----` parameters and return values indicate a **dependency**, while `<—<>` properties indicate **aggregation**.
4. Understand Spring's `BeanFactory`, `ApplicationContext`, `ApplicationListener`, and `Environment`, along with the four corresponding `Aware` interfaces.
4. Understand the dependency difference between `spring-web` and `spring-webmvc`: the former places a Spring application in a web environment, while the latter implements Spring's MVC model for the web.
5. In the narrow sense, Spring MVC has the server render the view. The widely adopted separation of frontend and backend, where the backend sends only JSON data for the frontend to render, does not belong to that narrow MVC model: the server converts the model directly to JSON rather than rendering a view. The source confirms that when Spring MVC returns JSON, its returned `ModelAndView` is empty. This led me to an idea: simplify Spring MVC.
