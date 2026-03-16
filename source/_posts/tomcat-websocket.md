---
title: "Tomcat中websocket的使用和原理"
tags:
   - Tomcat
   - Websocket
   - Java
categories:
   - 源码剖析
date: 2020-09-21 10:36
description: "深入剖析WebSocket协议在SpringBoot+Tomcat中的使用方式与底层实现原理。使用层面介绍@ServerEndpoint注解及@OnOpen、@OnClose、@OnMessage、@OnError等生命周期方法的配置与前后端完整示例代码；源码层面逐步分析启动流程（ServerEndpointExporter注册端点、WsServerContainer装载配置、PojoMethodMapping处理注解方法映射）和执行流程（WsFilter协议升级、WsHttpUpgradeHandler初始化Session、反射调用业务逻辑），并总结建造者模式、过滤器模式、模板方法模式和适配器模式等在其中的应用。"
---


WebSocket是基于tcp的一种全双工通信的协议，它在建立连接的时候需要使用http协议，之后开始连接之后会独立出来。通常，http的每次连接都需要建立在url之上，但是webSocket只需要一个url来建立握手。常见的webSocket有多种实现方式，如SpringBoot+tomcat，或者是springboot+netty

<!-- more -->


### 使用方式

> 以下的代码均是基于Spring+tomcat

首先会在socket那里协商ServerEndPoint注解，然后注解出几个方法，如@BeforeHandshake, @OnOpen, @OnClose, @OnMessage 等等，然后在这些注解方法当中实现响应的业务逻辑。之后在前端页面开启socket即可。
对于后台来说，每个链接都是一个session，一般我们会把每个用户的session保留下来，以此来实现一对一和一对多的通信


#### 1. 后台代码

```java
@Configuration
public class AppConfiguration {
    @Bean
    public ServerEndpointExporter serverEndpointExporter(){
        return new ServerEndpointExporter();
    }
}
@Component
@ServerEndpoint("/webSocket/{page}")
public class TomcatSocket {
    private final static Logger LOG = LoggerFactory.getLogger(TomcatSocket.class);
    @OnOpen
    public void open(@PathParam("page") String page, Session session) {
    }
    @OnClose
    public void close(@PathParam("page") String page, Session session){
    }
    @OnMessage
    public void receiveMessage(@PathParam("page") String page, Session session, String message) throws IOException {
        LOG.info("接受到用户{}的数据:{}",session.getId(),message);
    }
    @OnError
    public void error(Throwable throwable){
        try {
            throw throwable;
        } catch (Throwable e) {
            LOG.error("未知错误");
        }
    }
}
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>cn.wxxlamp</groupId>
    <artifactId>YeautyTest</artifactId>
    <version>1.0-SNAPSHOT</version>

    <!-- 定义公共资源版本 -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.0.1.RELEASE</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
        <java.version>1.8</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-websocket</artifactId>
        </dependency>
    </dependencies>
</project>
```

#### 2. 前端代码

```html
<html>
<head>
    <meta charset="UTF-8"/>
</head>
<input id="text" type="text" />
<button onclick="send()">发送测试</button>
<hr />
<button onclick="clos()">关闭连接</button>
<hr />
<div id="message"></div>
<script>
    var websocket = null;
    if('WebSocket' in window){
        websocket = new WebSocket("ws://127.0.0.1:8080/webSocket/1");
    }else{
        alert("您的浏览器不支持websocket");
    }
    websocket.onerror = function(){
        setMessageInHtml("send error！");
    }
    websocket.onopen = function(){
        setMessageInHtml("连接成功！")
        setTimeout(function(){setMessageInHtml("欢迎来到这里！")
        },2000)
    }
    websocket.onmessage = e => setMessageInHtml(e.data)
    websocket.onclose = function(){
        setMessageInHtml("连接断开！")
    }
    window.onbeforeunload = function(){
        clos();
    }
    function setMessageInHtml(message){
        document.getElementById('message').innerHTML += message+"</br>";
    }
    function clos(){
        websocket.close(3000,"强制关闭");
    }
    function send(){
        var msg = document.getElementById('text').value;
        websocket.send(msg);
    }
</script>
</body>
</html>
```

### 源码分析

使用的时候，我不禁有一个疑问，为什么加上这些注解就可以实现WebSocket的通信了呢？这里，通过springboot+tomcat的源码进行分析
首先先学习下Spring关于WebSocket的[文档](https://docs.spring.io/spring-framework/docs/5.3.0-SNAPSHOT/reference/html/web.html#websocket)，其中主要介绍了WebSocket和Http的区别，以及使用时机，同时还介绍了Spring结合WebSocket如何使用
首先我们发现，Java的webSocket主要依赖了两个jar包，一个是tomcat-embed-websocket，另一个是spring-websocket

#### 1. 启动流程

首先我们自定义了一个配置类，把 `ServerEndpointExporter` 注册为bean，然后这个bean在初始化的时候会进入registerEndPoints方法，找到包含@ServerEndPoint注解或者实现了ServerEndPointConfig接口的bean，然后把他们放入ServerContainer中
![image](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/35b692e6_tomcat-ws-img1.png)
可以发现，我们使用websocket的类都被注册到ServerContainer这个接口的实现类当中了，所以下一步的分析就是去找它的实现类（WsServerContainer）了，看它是如何处理这些注解的


现在去看WsServerContainer在addEndpoint时做了一个事情：主要是把注解中的配置装入ServerEndpointConfig类中，从而被系统识别。这其中用了Builder的建造者模式。这一步完成以后，我们可以发现，此时注解形成的和接口形成的配置全都被装载进了ServerPointConfig中，等于说把他们抽象出来了，然后就可以只处理ServerEndPointConfig了


那么下一步，就是去处理ServerPointConfig的配置了。处理那些配置呢？我们不妨想一下，肯定会处理方法中OnOpen这些注解（下图中进入PojoMethodMapping类中去处理方法的映射）：
![image](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/a6fd85e1_tomcat-ws-img2.png)
如下图，PojoMethodMapping确实是为了处理存放每个注解的方法以及他们的参数    
![image](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/281061d9_tomcat-ws-img3.png)

> 那么这里引入一个问题，如果A继承了B，然后A有@OnClose，B有@OnOpen，这样该如何选择呢？又或者，如果A和B都有@OnOpen，那么改选则哪一个呢？又或者，A有两个@OnClose，那么该怎么办呢？这个先不予解答，希望大家看下PojoMehodMapping的构造方法

在查看源码的过程中，我发现程序会定向识别几个方法的参数：OnOpen有EndpointConfig，OnClose有CloseReason，OnError有Throwable，然后他们需要识别Session和PathParam。方法参数是一个独自的类，叫PojoPathParam，它有两个属性，一个是参数的注解（即PathParam），一个是返回值
除此之外，它在识别OnMessage时，会使用内部类MessageHandlerInfo来进行配置


继续分析WsServerContainer的addEndPoint方法。
下一步，就是通过UriTemplate去处理映射的路由路径（此处通过TreeSet来排序和去重，以直接抛异常的方式），把uri和和其uriTemplate形成map




可以说，一个WebSocket对应着一个PojoMehodMapping。那么分析到这里为止，我们可以总结下：一个WebSocket的类，对应着一个PojoMethodMapping和UriTemplate，同时也对应着一个ServerEndPointConfig，然后WsServerContainer对应多个ServerEndPointConfig


到此为止，把所有的东西都注册完成并识别成功，那么下一步，就是执行流程了


#### 2. 执行流程


这里，我们不得不需要一些前置知识，即TOMCAT的执行流程，同时还应该学习一下SpringMVC是如何和tomcat集合的。**当然，socket和mvc没多大关系**
大体上来说，tomcat在启动后会一直监听我们设定的端口，当有http请求过来后，tomcat首先会解析http请求的header，body，url等等，然后通过url映射到相应的servlet，springMVC在这里做了一个事情，就是使得tomcat的所有映射都进入dispatcherServlet，然后再通过dispatcherServlet进入到对应的Controller中。_(这里也用到了适配器模式，具体可以看我的博客）_


这里的执行是利用filter来执行的，这里感兴趣的同学可以学习一下责任链模式。

对于Tomcat来说，它首先会通过ApplicationFilterChain去执行filter，此时会进入到WsFilter中去判断第一次连接，即upgrade请求（此时使用的http），之后调用servlet.service去到controller中执行


从执行来说，首先会进入socket连接，执行org.apache.coyote.AbstractProtocol.ConnectionHandler#process方法。在这个方法中然后再被过滤器过滤。过滤器会去判断它是不是websocket的连接，如果是，则升级协议，之后process方法会根据每次连接的状态来处理流程


那么，我们就从WsFilter开始去看它的执行流程把~
首先在handshake之前，会进入WsFilter中去升级协议（即给client的响应中协商改变协议）。在升级的过程中，它会把uri对应的ServerEndPointConfig，request，二阶段协商内容等等装入PojoEndpointServer中，这里面调用的是WsHttpUpgradeHandler的preinit方法。
![image](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/cc6b06c5_tomcat-ws-img4.png)
当WsFilter执行完之后，因为需要升级协议，所以他会在upgradeToken那里打上标记，记得之前执行了handler的preinit方法吗，这时，它就会去执行init方法，把这些配置全放到session中。
![image](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/eee80285_tomcat-ws-img5.png)
注意之前的PojoEndpointServer，它是执行我们自定义SocketServer的容器。在这个过程中，我们把自定义的pojo，即我们自己的socket放到了PojoEndpointServer，便于它进行最后的反射调用
![image](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/0e2a37b3_tomcat-ws-img6b.png)
以上就是OnOpen的执行流程。

那么下面分析OnMessage的执行流程：
首先我们回忆一下在执行流程中的onOpen阶段（即上图第50行），他会把含有OnMessage注解的Handler放到session中。
记得我们之前有一个WsHttpUpgradeHandler类吗，tomcat会根据连接的状态去调用WsHttpUpgradeHandler#upgradeDispatch的方法，然后这个方法会去通过WsFrameBase到session中拿到之前注册的handler（这里是ojoMessageHandlerWholeText），然后调用其onMessage方法，让后在这个方法中会通过反射调用其中的OnMessage方法，执行我们自己的逻辑
![image](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/675956fa_tomcat-ws-img7.png)

#### 3. 总结

总结一下，这次源码分析说是分析Spring+Tomcat，但是其实更多的核心代码还是在tomcat中，Spring-websocket只是起了自动装配的作用，初始化出对应的WsServerContainer之后就没有它的活了。
启动过程中，会结合Spring的生命周期去检测对应的注解或者接口，把对应的方法和类，uri装载到config和handler中
执行的时候，会先去通过tomcat自带的过滤器即filter去检测是否是websocket的upgrade模式，如果是，则和client升级协议，建立websocket连接。之后再通过反射去处理对应的业务逻辑
用的的设计模式有：建造者模式，过滤器模式，模板方法模式，适配器模式