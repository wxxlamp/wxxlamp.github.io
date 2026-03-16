---
title: "当调用多个IO操作时"
tags:
   - Concurrent
categories:
   - 场景实践
date: 2022-10-30 14:36
description: "探讨微服务Facade层聚合多RPC调用时如何将串行改为并行。对比Callable+Future、CompletableFuture、Spring Event三种方案，分析最终一致性保障及线程池配置实践。"
---

## 0. 前言

在微服务系统中，各个域都有自己的服务模块承接。同时，在后端的Facade层中，会负责聚合各种微服务，然后再把聚合的结果返回给上游。在聚合的过程中，可能聚合的数据源不是互相依赖的，那么我们就可以转串行为并行，来提高Facade服务的RT。<br />举个栗子：营销系统判断该用户是否有权限领券，在判断权限的过程中，需要做这几件事情：

1. 请求风控系统判断该用户是否在黑名单中
2. 请求业务系统A用户是否有开通某领券服务（领券的前置条件），etc

那么对于这几件事情，可以认为这些调用都是互相没有关系的，所以我们可以舍弃之前的串行调用方式，改用并行调用，本章即是讨论并行调用的几种方式，并简要分析。
## 1. 线程池处理
因为需要获取返回值，所以普通的Runnable一定是不行的，需要去实现Callable接口才可以，然后将远程执行的RPC任务放到线程池中，轮训每次的调用结果，并将结果放到集合中，如果所有的异步任务处理完成，则进行汇总，然后返回到调用方，示例代码如下：
```java
// 调用方法
public static void testWithThread(List<String> ret) {
    List<CallableTask> rpcs = ImmutableList.of(new CallableTask("1"), new CallableTask("2"),
                new CallableTask("3"),new CallableTask("4"));
    Queue<Future<String>> list = rpcs.stream()
                .map(ThreadPoolConfig.EXECUTOR::submit)
                .collect(Collectors.toCollection(Lists::newLinkedList));
    while (!list.isEmpty()) {
        String ans = null;
        Future<String> poll = list.poll();
        try {
            ans = poll.get(100, TimeUnit.MILLISECONDS);
        } catch (TimeoutException | InterruptedException | ExecutionException e) {
            System.out.println("time out");
            list.offer(poll);
        }
        if (ans != null) {
            ret.add(ans);
        }
    }
}
// 模拟RPC任务
public class CallableTask implements Callable<String> {

    private String ans;

    public CallableTask (String ans) {
        this.ans = ans;
    }
    @Override
    public String call() throws Exception {
        Thread.sleep(1000L);
        return ans;
    }
}
```
但是如上所示，由调用者去轮训且将未完成的Future放到队列中重新轮训去获得结果显然不够优雅，所以还需要对线程的编排进一步优化
## 2. CompletableFuture
正是因为线程编排和获取返回值太过于麻烦，所以Java8之后有了`CompletableFuture`类去协助我们做线程编排
```java
public static List<String> testWithCompleteFuture(List<String> ret) {
    List<CallableTask> rpcs = ImmutableList.of(new CallableTask("1"), new CallableTask("2"),
                new CallableTask("3"),new CallableTask("4"));
    List<CompletableFuture<String>> collect = rpcs.stream()
                .map(e -> CompletableFuture.supplyAsync(e, ThreadPoolConfig.EXECUTOR).whenComplete(((s, throwable) -> ret.add(s))))
                .collect(Collectors.toList());
    CompletableFuture.allOf(collect.toArray(new CompletableFuture[]{})).join();
}
```
但是CompletableFuture最大的作用并不是如上所述简单的并行调度，它更强大的功能是各种任务调用的编排，譬如先并行执行a，b，c三个任务，等任务执行完之后，再执行d任务等，在此只是抛砖引用，具体的高阶功能不再赘述
## 3. One More Thing
其实上文中说的主要是需要获取并行调用结果的情况，还有一种情况也很常见，就是后置通知的流程，它不需要获取Provider的响应来提供给上游，仍然举个栗子：用户开通某服务之后，服务管理系统需要处理这几件事情：

1. 将用户的资料存入用户信息系统
2. 通知关联业务用户已经开通
3. 将用户的附加信息进行标记，etc
> 注意：下面的讨论，建立在这些后置处理的事情，是和主业务保持最终一致性，而不是强一致性，譬如不存在用户资料存储失败，就算是开通失败

对于这些处理，上游的调用方是不需要感知到的，一般有两种处理方式，第一种是本地系统直接发送消息，由下游系统订阅并处理，第二种方式是本地系统直接调用下游的RPC服务，直接处理流程。本段主要讨论第二种方式。<br />并发调用的时候，可以使用上文中提到的线程池或者直接用CompletableFuture进行线程编排。另一种方式是使用Spring Event来完成后置通知，但是对于Spring Event来说，它本身是同步的，需要结合Spring Async的能力进行异步化。<br />尤其要注意的是，不管使用哪种方式，一定要考虑调用失败的场景（如服务找不到，调用超时，调用服务内部异常等），因为是要保证最终一致性，可以把调用失败的上下文落库，等待定时调度任务重试即可<br />不过要说明的是，不能只用Spring的Async注解，因为Spring的异步能力默认是一个方法新开一个线程，当异步Listener过多的是时候，容易导致线程的OOM，所以此时需要我们自定义线程池去复用，一个简单的例子如下：
```java
// 调用
@Component
public class Client {
    
    @Autowired
    private ApplicationEventPublisher publisher;

    public void invoke() {
        SpringEvent springEvent = new SpringEvent();
        publisher.publishEvent(springEvent);
    }

}
// 监听
@Component
public class Listener {

    @EventListener
    @Async
    public void test1(SpringEvent event) {
        String name = Thread.currentThread().getName();
        System.out.println(event + name + " 111 " + System.currentTimeMillis());
    }

    @EventListener
    @Async
    public void test2(SpringEvent event) {
        String name = Thread.currentThread().getName();
        System.out.println(event + name + " 222 " + System.currentTimeMillis());
    }
}
// 配置
@EnableAsync
@Configuration
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor taskExecutor = new ThreadPoolTaskExecutor();
        taskExecutor.setCorePoolSize(2);
        taskExecutor.setMaxPoolSize(10);
        taskExecutor.setQueueCapacity(15);
        taskExecutor.setThreadNamePrefix("async-thread-");
        taskExecutor.initialize();
        return taskExecutor;
    }

    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return this::processException;
    }

    private void processException(Throwable throwable, Method method, Object... objects) {
        // 上下文落库，等待定时任务唤醒重试
    }
}
```

