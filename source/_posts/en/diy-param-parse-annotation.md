---
title: Building a Custom Parameter Parser for Spring MVC
date: 2020-12-22 18:26
tags:
  - Spring 框架
  - Java
categories:
  - 场景实践
description: >-
  Solving the problem that @RequestBody cannot map multiple parameters in Spring
  MVC by implementing a custom HandlerMethodArgumentResolver and annotation to
  map JSON fields precisely to multiple parameters.
lang: en
translation_of: diy-param-parse-annotation
---

During my internship, most of the company's RESTful requests were GET and POST requests. For parameters carried in a URL, we use `@PathVariable` and `@RequestParam` to parse and map them. For a POST body, we use `@RequestBody` to map the body to parameters. Spring deserializes with Jackson by default, though we can change this with a converter.

### 1. Start with an experiment

For a POST request, the frontend often serializes parameters as JSON in the body. The backend then parses the JSON string with `@RequestBody` and maps it to method parameters. `@RequestBody` has a limitation, as we can see from this example:

```java
@PostMapping("/1")
public String test(@RequestBody String a, @RequestBody String b) {
    return a + b;
}
```

In the HTTP request, set the method to POST and the body to:

```json
{
    "a":"a",
    "b":"b"
}
```

We naturally expect the program to parse a as `a`, b as `b`, and return “ab”. After running it, however, the program returns “abab”. Debugging shows that `@RequestBody` parses a as “ab” and b as “ab” as well.

The experiment reveals the problem: after parsing the body, `@RequestBody` can map the result to only one parameter. When there are two parameters, it reaches its limits.

### 2. Solution

To solve this problem, we must turn the parameters into one. There are two ways:

1. Wrap both parameters in an entity class.

   ```java
   @PostMapping("/1")
   public String test(@RequestBody Ab ab) {
       return ab.getA() + ab.getB();
   }
   ```

2. Wrap them in a Map and parse it.

   ```java
   @PostMapping("/1")
   public String test(@RequestBody Map<String, Object> map) {
       return map.get("a") + map.get("b");
   }
   ```

Both approaches have problems. With the first, we must create a new Bean to aggregate the two parameters, increasing development cost. With the second, we must parse the Map, increasing the cost of understanding the code.

Could we map the body to two or more parameters? That is the core of this article: DIY a parameter parser to replace `@RequestBody` and map the body to multiple parameters.

### 3. DIY the parameter parser

Looking at the parsing source code for `@RequestBody`, we can see that `RequestResponseBodyMethodProcessor` performs body parsing and mapping. Looking further up, it implements the `HandlerMethodArgumentResolver` interface, which Spring exposes to help users customize parameter parsing. So our first step is:

```java
// 接口的第一个方法，如果返回为true，则使用该解析器，第二个方法则是具体的解析流程
@Component
public class RequestBodyParamProcessor implements HandlerMethodArgumentResolver{

    @Override
    public boolean supportsParameter(MethodParameter parameter) {
        return false;
    }

    @Override
    public Object resolveArgument(MethodParameter parameter, ModelAndViewContainer mavContainer, NativeWebRequest webRequest, WebDataBinderFactory binderFactory) throws Exception {
        return null;
    }
}
```

Second, add this parser to the parsing chain:

```java
@Configuration
public class Config implements WebMvcConfigurer {
    @Autowired
    private RequestBodyParamProcessor paramProcessor;

    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
        resolvers.add(this.paramProcessor);
    }
}
```

These two steps give us the basic framework.

Third, define a custom annotation. If the user marks a method with it, the parameters should be parsed using our custom approach.

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RequestBodyParam {
}
```

Fourth, implement the parsing logic. By reading `RequestResponseBodyMethodProcessor`, I found that it parses the body through `AbstractMessageConverterMethodArgumentResolver#readWithMessageConverters`. We can therefore write the following:

```java
@Component
public class RequestBodyParamProcessor
        extends AbstractMessageConverterMethodArgumentResolver implements HandlerMethodArgumentResolver{

    public RequestBodyParamProcessor(List<HttpMessageConverter<?>> converters) {
        super(converters);
    }

    /**
     * 如果有该注解，且方法为String类型则使用该Processor
     * @param parameter 方法参数
     * @return true/false
     */
    @Override
    public boolean supportsParameter(MethodParameter parameter) {
        return parameter.hasMethodAnnotation(RequestBodyParam.class) &&
                parameter.getParameterType() == String.class;
    }

    @Override
    public Object resolveArgument(MethodParameter parameter, ModelAndViewContainer mavContainer, NativeWebRequest webRequest, WebDataBinderFactory binderFactory) throws Exception {
        HttpServletRequest servletRequest = webRequest.getNativeRequest(HttpServletRequest.class);
        assert servletRequest != null;
        ServletServerHttpRequest inputMsg = new ServletServerHttpRequest(servletRequest);

        Object body = readWithMessageConverters(inputMsg, parameter, Map.class);
        ObjectMapper mapper = new ObjectMapper();
        Map<String, String> kv = mapper.readValue((String) body, new TypeReference<Map<String,String>>() {});
        return kv.get(parameter.getParameterName());
    }
}
```

At this point, our custom parameter parser is complete.

Fifth, test it:

```java
@PostMapping("/1")
@RequestBodyParam
public String test(String a, String b) {
    return a + b;
}
```

Passing the same parameters as in the earlier experiment returns “ab”. Debugging shows a=“a” and b=“b”, as required.

### 4. Afterword

While developing at my internship company, I found that, because of an earlier company convention, everyone used POST requests for everything: idempotent information retrieval, updates, and even deletion. This clearly did not follow the standard, but that is another story.... The result was that when the frontend needed to retrieve information, it often sent only a few parameters wrapped in JSON in the body. If I used `@RequestBody`, I could use only the two approaches above, which led me to DIY a parameter parser. That is where this article came from.

Note, however, that this parser is still toy-level. It can parse only JSON strings whose body values are String, and it is still a long way from being truly practical.....



2021.1.27 update:

I later wrote an article on [@RequestBody parsing](https://wxxlamp.cn/en/2021/01/27/annotation-requestbody/) that may help with understanding.
