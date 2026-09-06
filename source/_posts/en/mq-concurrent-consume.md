---
title: Analyzing Multithreaded Consumption in RocketMQ
tags:
  - 消息队列
  - 并发编程
  - 问题排查
categories:
  - 采坑记录
date: 2021-8-07 14:36
description: >-
  A record of troubleshooting a production incident in which RocketMQ
  consumption success rates suddenly dropped. It locates
  ConcurrentModificationException, analyzes ArrayList's fail-fast mechanism and
  concurrent sort/forEach access, and summarizes thread-safety principles.
lang: en
translation_of: mq-concurrent-consume
---

The first time the project was released to the gray-release machines, something went wrong. Here is a record of it:

### Background

After the system was released, monitoring began to alert us that RocketMQ's consumption success rate was around 30%, clearly below 100%.

My initial analysis was that the lower rate might be caused by:

1. Too many log messages piling up at the consumer, which could not consume them and discarded them directly.
2. An exception in the consumer code, meaning consumption did not succeed and the exception was caught by MQ.
3. The consumer returning `*RECONSUME_LATER*`, requiring the message to be consumed later.

After checking the monitoring reports, I found that the JVM and OS were behaving normally, so the system did have the capacity to consume messages; case 1 was ruled out. The code also had no situation that could return “consume later,” so case 3 was ruled out. That left only case 2.

The MetaQ logs showed this:

```shell
WARN RocketmqClient - consumeMessage exception: java.util.ConcurrentModificationException, java.util.ArrayList.forEach(ArrarayList.java:1260) 
```

The system had thrown a `ConcurrentModificationException`. At this point, it was essentially certain that multiple threads were accessing the system. This exception is fundamentally related to concurrent modification of a collection, so the cause was almost confirmed.

The problematic code was:

```java
public class Main {

    public static void main(String[] args) {
        List<Integer> list = new ArrayList<>(Arrays.asList(1, 3, 4, 2));
        ThreadPoolExecutor threadPool = new ThreadPoolExecutor(
                10, 10, 20, TimeUnit.SECONDS, new ArrayBlockingQueue<>(10),
                new ThreadPoolExecutor.DiscardOldestPolicy());
        while (true) {
            try {
                threadPool.execute(() -> {
                    list.sort(Comparator.comparingInt(o -> o));
                    list.forEach(System.out::println);
                });
            } catch (ConcurrentModificationException e) {
                System.out.println(e.getMessage());
                break;
            }
        }

    }
}
```

### Cause

The problem occurred because multiple threads accessed the list, performing both `sort` and `forEach`. This triggered the list's fail-fast mechanism. The source code is:

```java
@SuppressWarnings("unchecked")
public void sort(Comparator<? super E> c) {
    final int expectedModCount = modCount;
    Arrays.sort((E[]) elementData, 0, size, c);
    if (modCount != expectedModCount) {
        throw new ConcurrentModificationException();
    }
    modCount++;
}

public void forEach(Consumer<? super E> action) {
    Objects.requireNonNull(action);
    final int expectedModCount = modCount;
    @SuppressWarnings("unchecked")
    final E[] elementData = (E[]) this.elementData;
    final int size = this.size;
    for (int i=0; modCount == expectedModCount && i < size; i++) {
        action.accept(elementData[i]);
    }
    if (modCount != expectedModCount) {    
        throw new ConcurrentModificationException();
    }
}
```

Fail-fast means that the collection records the number of operations when it starts being traversed. If another thread writes to it during traversal, the operation count increases; the system then assumes that concurrent access has occurred and throws `ConcurrentModificationException`.

### Solution

1. Do not use a thread-unsafe collection.
2. With a thread-unsafe collection, do not perform both a read operation such as `forEach` and a write operation such as `sort`; otherwise the list's fail-fast mechanism will be triggered.
3. More generally, for multithreaded consumption, thread safety must be guaranteed. Access to shared variables must be valid across threads. There are many ways to do this, such as using `sync`, `threadLocal`, and `final` semantics.

Sigh. I knew about fail-fast, but I never expected to step into this pitfall myself. Sucks.
