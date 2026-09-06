---
title: Coordinating Multiple I/O Calls in Java
tags:
  - Java
  - 并发编程
  - 性能优化
categories:
  - 场景实践
date: 2022-10-30 14:36
description: >-
  Explores how a microservice Facade layer can change aggregated RPC calls from
  serial to parallel. Compares Callable+Future, CompletableFuture, and Spring
  Event approaches, and discusses eventual-consistency safeguards and
  thread-pool configuration.
lang: en
translation_of: multi-rpc-return
---

## 0. Introduction

In a microservice system, every domain has its own service module. The backend Facade layer aggregates those microservices and returns the combined result upstream. When the data sources being aggregated do not depend on one another, serial calls can be made parallel to improve the Facade service's RT.<br />For example, when a marketing system determines whether a user may claim a coupon, it needs to:

1. Call the risk-control system to determine whether the user is blacklisted.
2. Call business system A to determine whether the user has enabled a coupon-claiming service (a prerequisite for claiming coupons), etc.

These calls are independent, so we can abandon the former serial approach for parallel calls. This article discusses and briefly analyzes several ways to do that.

## 1. Thread-pool handling

Because return values are needed, an ordinary `Runnable` is insufficient; the `Callable` interface must be implemented. Put the remotely executed RPC tasks in a thread pool, poll each result, put results into a collection, and aggregate them once all asynchronous tasks finish before returning to the caller. For example:

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

However, making the caller poll and requeue unfinished `Future`s is clearly inelegant, so task orchestration needs further improvement.

## 2. CompletableFuture

Because thread orchestration and obtaining return values are cumbersome, Java 8 introduced `CompletableFuture` to help with orchestration.

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

`CompletableFuture` is not most valuable simply for this sort of parallel scheduling. Its more powerful capability is composing task calls—for example, running tasks a, b, and c in parallel and then running d after they complete. This is only an introduction; its advanced functions are not covered here.

## 3. One More Thing

The discussion above concerns cases where results from parallel calls are needed. Another common case is a post-notification flow: the provider's response is not needed upstream. For example, after a user enables a service, a service-management system needs to:

1. Store the user's profile in the user-information system.
2. Notify related businesses that the user has enabled the service.
3. Mark the user's additional information, etc.

> Note: the following discussion assumes these post-processing actions require eventual consistency with the primary business, not strong consistency. For example, a failure to store user information does not mean that enabling the service failed.

The upstream caller need not be aware of these actions. There are usually two approaches: the local system sends a message that downstream systems subscribe to and process, or it directly calls downstream RPC services to process the flow. This section discusses the second approach.<br />For concurrent calls, use the thread pool above or `CompletableFuture` for task orchestration. Another option is Spring Event for post-notification, but Spring Event itself is synchronous and must be combined with Spring Async to become asynchronous.<br />Whichever method is used, failures (such as a missing service, timeout, or internal service exception) must be considered. To guarantee eventual consistency, persist the failed call's context and let a scheduled task retry it.<br />It is also important not to use only Spring's `Async` annotation. By default, Spring's async capability opens a new thread per method; too many async listeners can cause thread OOM. Define a reusable thread pool instead, as in this simple example:

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
