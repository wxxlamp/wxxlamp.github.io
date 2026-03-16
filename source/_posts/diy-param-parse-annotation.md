---
title: "DIY一个参数解析器"
date: 2020-12-22 18:26
tags:
   - Java
   - SpringMVC
categories:
   - 场景实践
description: "针对Spring MVC中@RequestBody无法将请求体映射到多个独立参数的局限，通过实现HandlerMethodArgumentResolver接口自定义参数解析器，结合自定义注解@RequestBodyParam，复用AbstractMessageConverterMethodArgumentResolver的消息转换能力，实现将POST请求body中的JSON字段精准映射到多个String类型方法参数的功能，从实验出发到完整代码实现，并说明其在公司全POST接口场景下的实际应用背景。"
---

在公司实习中，公司原有代码的RESTful请求中，GET和POST居多。我们知道，对于URL携带的参数来说，我们需要用`@PathVariable`，`@RequestParam`来进行解析和映射。对于POST的body来说，我们可以通过`@RequestBody`来把body映射到参数中，Spring默认的反序列化方式是通过Jackson，我们也可以通过converter来改变。

### 1. 从一个实验开始

对于POST请求来说，前端往往会把参数序列化为Json放到body中，然后我们后端再通过`@RequestBody`对body中的json串进行解析，之后再映射到方法的参数当中。而`@RequestBody`有一个弊端，我们通过下面的例子来观察一下：

```java
@PostMapping("/1")
public String test(@RequestBody String a, @RequestBody String b) {
    return a + b;
}
```

我们在Http请求中，把方法设为POST，然后把body设为：

```json
{
    "a":"a",
    "b":"b"
}
```

显然，我们期望程序可以把a解析为a，把b解析为b，然后返回“ab”。但是运行之后，我们发现，程序返回的是“abab”。通过debug我们可以发现，`@RequestBody`把a解析为“ab”，把b也解析成了“ab”。

从上面的实验我们可以发现一个问题：`@RequestBody`解析body后，只能把解析的结果映射到一个参数里面，如果出现两个参数，`@RequestBody`就后继乏力了。

### 2. 解决方案

要解决上面的问题，我们必须把参数变成一个，目前我们有两种方案来实现：

1. 把两个参数封装为一个实体类

   ```java
   @PostMapping("/1")
   public String test(@RequestBody Ab ab) {
       return ab.getA() + ab.getB();
   }
   ```

2. 通过Map封装，然后解析

   ```java
   @PostMapping("/1")
   public String test(@RequestBody Map<String, Object> map) {
       return map.get("a") + map.get("b");
   }
   ```

但是，这两种方案都有一定的问题。对于第一种方案来说，我们需要重新建一个Bean来将这两个参数聚合成一个，增加了我们的开发成本；对于第二种方案来说，我们需要在map中进行解析，增加了我们的理解成本。

有没有这样一种可能，将Body映射成两个甚至多个参数呢？这便是本文的核心——通过DIY一个参数解析器来代替@RequestBody实现body到多个参数的映射。

### 3. DIY参数解析器

通过查阅`@RequestBody`的解析源码可以发现，它通过`RequestResponseBodyMethodProcessor`这个类来实现对Body的解析和映射工作，那么再往上查看，其实现了`HandlerMethodArgumentResolver`接口，而这个接口就是Spring开放出来的，帮助用户自定义参数解析方式的接口，所以，我们第一步可以这样写：

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

第二步，我们需要把这个解析器添加到解析链路中：

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

这两部就可以帮助我们把框架搭建起来。

第三步，我们需要自定义一个注解，如果用户在方法上标明了该注解，则说明需要按照我们自定义的方式去解析

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RequestBodyParam {
}
```

第四步，就是去实现我们自己的解析逻辑。这里有个点，通过阅读`RequestResponseBodyMethodProcessor`源码，我发现，其解析body是通过`AbstractMessageConverterMethodArgumentResolver#readWithMessageConverters`方法进行解析，所以，我们可以写出如下解析过程：

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

当完成这一步的时候，我们自定义的参数解析器就完成了。

第五步，测试一下：

```java
@PostMapping("/1")
@RequestBodyParam
public String test(String a, String b) {
    return a + b;
}
```

按照之前实验的参数进行传入，返回值是“ab”。Debug发现，a=“a”，b=“b"，符合需求。

### 4. 后记

当我在实习公司进行开发的时候发现，由于公司之前的约定，大家无论是幂等的获取信息，还是修改信息，甚至是删除信息，都用的POST请求，这显然是不合规范的，但是事已至此，这就是另一个故事了。。。而这产生出来了一个问题，当前端需要获取信息的时候，它往往只传过来几个参数，把他们通过Json的格式封装到body中给我，而我如果使用`@RequestBody`，则只能用上面两种方法，所以，就想着DIY一个参数解析器，这便是这篇文章的由来。

不过需要注意的是，这个参数解析器还是玩具级别的，它只能解析body中value为String的json串，离真正实用还有着相当长的路要走......



2021.1.27更新：

新写了一篇[@ResponseBody解析](https://wxxlamp.cn/2021/01/27/annotation-requestbody/)的文章，有助于理解