---
title: "@RequestBody的原理"
tags:
   - JAVA
   - SPRING MVC
categories:
   - 源码剖析
date: 2021-01-27 10:36
description: "深入剖析SpringMVC中@RequestBody注解的底层原理，追踪执行链路、参数解析器注册流程，分析设计模式应用及缓存优化机制，附常见MVC参数注解对比。"
---

通过Http传递参数一般有两种方式，一种是通过url解析参数，一种是通过body来解决，那么我们本次说的RequestBody就是去解析请求体然后映射到我们的参数，那 么它该如何解析body呢？这就是本篇博客诞生的目的。

<!--more-->

这个其实是SpringMVC中做的一个处理机制，在整个SpringMVC的处理流程中，会通过HandlerMethod来代理每个Map后的controller和method，在通过反射invoke method的过程中，会解析request来获得arguments，而@RequestBody就是在解析参数的这个过程中起作用的

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/98f5a38e_annotation-requestbody-1.png" align="middle" />

### 壹. 执行流程

在`InvocableHandlerMethod#getMethodArgumentValues`中，它会遍历当前HandlerMethod的参数，对于每一个参数，它都会通过`HandlerMethodArgumentResolverComposite#supportsParameter`来判断是否可以被解析器解析，如果可以被解析，则通过`HandlerMethodArgumentResolverComposite#resolveArguement`进行解析

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/94db22f0_annotation-requestbody-2.png" align="middle" />

对于@RequestBody来说，它对应的解析器是`RequestResponseBodyMethodProcessor`，那么，我们就深入到它的源码中来一探究竟:

```java
public class RequestResponseBodyMethodProcessor extends AbstractMessageConverterMethodProcessor {

	// 是否可以解析当前参数
	@Override
	public boolean supportsParameter(MethodParameter parameter) {
		return parameter.hasParameterAnnotation(RequestBody.class);
	}

    // 是否可以解析当前返回值
	@Override
	public boolean supportsReturnType(MethodParameter returnType) {
		return (AnnotatedElementUtils.hasAnnotation(returnType.getContainingClass(), ResponseBody.class) ||
				returnType.hasMethodAnnotation(ResponseBody.class));
	}

	
	@Override
	public Object resolveArgument(MethodParameter parameter, @Nullable ModelAndViewContainer mavContainer,
			NativeWebRequest webRequest, @Nullable WebDataBinderFactory binderFactory) throws Exception {

		parameter = parameter.nestedIfOptional();
        // 解析handlerMethod中的参数
		Object arg = readWithMessageConverters(webRequest, parameter, parameter.getNestedGenericParameterType());
        // 获取变量名
		String name = Conventions.getVariableNameForParameter(parameter);

		if (binderFactory != null) {
			WebDataBinder binder = binderFactory.createBinder(webRequest, arg, name);
			if (arg != null) {
                // 通过binder校验@Validated注解的字段
				validateIfApplicable(binder, parameter);
				if (binder.getBindingResult().hasErrors() && isBindExceptionRequired(binder, parameter)) {
					throw new MethodArgumentNotValidException(parameter, binder.getBindingResult());
				}
			}
			if (mavContainer != null) {
				mavContainer.addAttribute(BindingResult.MODEL_KEY_PREFIX + name, binder.getBindingResult());
			}
		}

        // 如果方法是Optional参数，则代理
		return adaptArgumentIfNecessary(arg, parameter);
	}

	@Override
	protected <T> Object readWithMessageConverters(NativeWebRequest webRequest, MethodParameter parameter,
			Type paramType) throws IOException, HttpMediaTypeNotSupportedException, HttpMessageNotReadableException {

		HttpServletRequest servletRequest = webRequest.getNativeRequest(HttpServletRequest.class);
		Assert.state(servletRequest != null, "No HttpServletRequest");
		ServletServerHttpRequest inputMessage = new ServletServerHttpRequest(servletRequest);

        // 解析http请求中的body并映射到对应的parameter上
		Object arg = readWithMessageConverters(inputMessage, parameter, paramType);
		if (arg == null && checkRequired(parameter)) {
			throw new HttpMessageNotReadableException("Required request body is missing: " +
					parameter.getExecutable().toGenericString());
		}
		return arg;
	}

	protected boolean checkRequired(MethodParameter parameter) {
		RequestBody requestBody = parameter.getParameterAnnotation(RequestBody.class);
		return (requestBody != null && requestBody.required() && !parameter.isOptional());
	}


}
```

### 贰. 注册流程

那么`RequestResponseBodyMethodProcessor`是如何被注册到resolver中呢？主要是在`RequestMappingHandlerAdapter`中：

> `RequestMappingHandlerAdapter`实现了`HandlerAdapter`这个接口，这个接口是MVC框架的SPI，`DispatcherServlet`通过此接口访问所有已安装的处理程序。
>
> HandlerAdapter主要是路由之后方法的适配器，DispatcherServlet在路由之后通过HandlerAdapter来执行真实的操作（handlerAdapter是通过HandlerMethod来执行的）

对于`RequestResponseBodyMethodProcessor`来说，它实现了`InitializingBean`，在bean初始化之后会添加参数处理器和返回值处理器，对于参数处理器来说，内容如下：

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/9fc9e5f8_annotation-requestbody-3.png" align="middle" />

从图中我们可以看到，`RequestMappingHandlerAdapter`在初始化的时候会把系统给定的，自定义的参数解析器加载到内存中。

加入说，我们要自定义一个参数解析器，系统会在什么时候加载进入内存呢？

我们发现`RequestMappingHandlerAdapter#setCustomArgumentResolvers`这个方法就是要去设置自定义参数解析器的，那么我们只需要找到它的调用方即可。

我们只需要实现WebMvcConfigurer即可（这点关系到Spring的自动装配，暂时没有看到，先鸽一下）

### 叁. 设计优点

#### 设计模式

采用策略模式＋工厂模式 + 组合模式：

对于HandlerMethod的参数和返回值处理来说，对应着不同的处理方式，即对应着不同的策略，所以此处用的策略模式来处理的。至于`HandlerMethodArgumentResolverComposite`它则对应着策略工厂，同时，因为这个类实现了`HandlerMethodArgumentResolver`，所以它也是组合模式的变形，具体的策略类是`HandlerMethodArgumentResolver`

类图如下：

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/0401ebb4_annotation-requestbody-4.png" align="middle" />

#### 缓存处理

在参数解析工厂中，刚开始的参数解析器是在刚启动时注册到list中，但是如果之后被使用的时候就会存放到map中，可以直接获得(key是MethodParam)，提高路由效率

### 附：常见的MVC参数注解

对于url解析参数来说，有两个注解，分别是`pathVariable`（指一种占位符）和`requestParam`,对于body来说，有`requestBody`。不加注解，也可以直接把url转为对应参数或者实体类

1. @PathVariable: www.666.com/web/6 

```java
@GetMapping("/web/{node}")
public ReturnType listEmployeeInNode(@PathVariable String node) throws BusinessException {
}
```

2. @ReqeustParam: www.666.com/web?user=1

```java
@GetMapping("/web")
public ReturnType listEmployeeInNode(@RequestParam("user") String node) throws BusinessException {
}
```

3. @RequestBody: www.666.com/web  body中是json

```java
@GetMapping("/web")
public ReturnType listEmployeeInNode(@RequestBody UserDTO userDto) throws BusinessException {
}
```

4. 无注解：www.666.com/web?userId=1&pwd=2

```java
@PostMapping("/web")
public ReturnType listEmployeeInNode(UserDTO userDto) throws BusinessException {
}
```

[link](https://cloud.tencent.com/developer/article/1611093)