---
title: How Spring MVC Resolves @RequestBody Parameters
tags:
  - Spring 框架
  - Java
categories:
  - 源码剖析
date: 2021-01-27 10:36
description: >-
  A deep dive into the internals of Spring MVC's `@RequestBody` annotation,
  tracing the execution path, parameter resolver registration flow, design
  patterns, and caching optimizations, with a comparison to common MVC
  parameter annotations.
lang: en
translation_of: annotation-requestbody
---

There are generally two ways to pass parameters through HTTP: parse them from the URL, or place them in the body. What we are discussing here is `RequestBody`, which parses the request body and maps it to our parameters. So how does it parse the body? That is the purpose of this article.

<!--more-->

This is actually a processing mechanism inside Spring MVC. In the overall Spring MVC request flow, each mapped controller and method is proxied through `HandlerMethod`, and during the reflective `invoke` call on the method, Spring parses the request to obtain the arguments. `@RequestBody` plays its role during this parameter parsing process.

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/98f5a38e_annotation-requestbody-1.png" align="middle" />

### 1. Execution Flow

In `InvocableHandlerMethod#getMethodArgumentValues`, it iterates over the parameters of the current `HandlerMethod`. For each parameter, it uses `HandlerMethodArgumentResolverComposite#supportsParameter` to determine whether the parameter can be resolved by a resolver. If it can, it uses `HandlerMethodArgumentResolverComposite#resolveArguement` to resolve it.

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/94db22f0_annotation-requestbody-2.png" align="middle" />

For `@RequestBody`, the corresponding resolver is `RequestResponseBodyMethodProcessor`. Let us go into its source code and take a closer look:

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

### 2. Registration Flow

So how is `RequestResponseBodyMethodProcessor` registered into the resolver list? This mainly happens in `RequestMappingHandlerAdapter`:

> `RequestMappingHandlerAdapter` implements the `HandlerAdapter` interface. This interface is the SPI of the MVC framework, and `DispatcherServlet` uses it to access all installed handlers.
>
> `HandlerAdapter` is mainly the adapter for routed methods. After routing, `DispatcherServlet` uses `HandlerAdapter` to execute the real operation (`handlerAdapter` works through `HandlerMethod`).

For `RequestResponseBodyMethodProcessor`, it implements `InitializingBean`. After bean initialization, it adds parameter handlers and return value handlers. For the parameter handlers, the content is as follows:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/9fc9e5f8_annotation-requestbody-3.png" align="middle" />

From the figure, we can see that `RequestMappingHandlerAdapter` loads the framework-provided and custom parameter resolvers into memory during initialization.

Suppose we want to customize a parameter resolver. When will the system load it into memory?

We find that `RequestMappingHandlerAdapter#setCustomArgumentResolvers` is the method used to set custom parameter resolvers, so we only need to find its caller.

We only need to implement `WebMvcConfigurer` (this relates to Spring's auto-configuration, which I have not looked into yet, so I will leave it aside for now)

### 3. Design Advantages

#### Design Patterns

It uses the strategy pattern + factory pattern + composite pattern:

For parameter and return value handling in `HandlerMethod`, different handling strategies correspond to different types of processing, so the strategy pattern is used here. As for `HandlerMethodArgumentResolverComposite`, it corresponds to a strategy factory. At the same time, because this class implements `HandlerMethodArgumentResolver`, it is also a variant of the composite pattern, and the concrete strategy class is `HandlerMethodArgumentResolver`.

The class diagram is shown below:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/0401ebb4_annotation-requestbody-4.png" align="middle" />

#### Caching

In the parameter resolution factory, the resolvers are registered into a list when the application first starts. But if they are used later, they are stored in a map and can be retrieved directly (with `MethodParameter` as the key), improving routing efficiency.

### Appendix: Common MVC Parameter Annotations

For URL parameter parsing, there are two annotations: `pathVariable` (a type of placeholder) and `requestParam`. For the body, there is `requestBody`. Even without annotations, the URL can also be directly converted into the corresponding parameter or entity class.

1. @PathVariable: www.666.com/web/6 

```java
@GetMapping("/web/{node}")
public ReturnType listEmployeeInNode(@PathVariable String node) throws BusinessException {
}
```

2. @RequestParam: www.666.com/web?user=1

```java
@GetMapping("/web")
public ReturnType listEmployeeInNode(@RequestParam("user") String node) throws BusinessException {
}
```

3. @RequestBody: www.666.com/web  the body contains JSON

```java
@GetMapping("/web")
public ReturnType listEmployeeInNode(@RequestBody UserDTO userDto) throws BusinessException {
}
```

4. No annotation: www.666.com/web?userId=1&pwd=2

```java
@PostMapping("/web")
public ReturnType listEmployeeInNode(UserDTO userDto) throws BusinessException {
}
```

[link](https://cloud.tencent.com/developer/article/1611093)
