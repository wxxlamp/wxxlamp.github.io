---
title: "RocketMQ多线程消费问题分析"
tags:
   - Concurrent
   - MQ
categories:
   - 采坑记录
date: 2021-8-07 14:36
description: "记录RocketMQ消费成功率异常的排查过程，分析并发消费场景下的问题与解决方案。"
---

第一次项目发布到灰度的机器就出问题了，记录一下：

### 问题背景

系统发布后，监控开始报警，提示RocketMQ的消费成功率在30%左右，明显小于100%

初步分析，消费成功率变低的原因可能是：

1. 因为日志消息太多，导致消费端堆积，没有能力消费直接抛掉
2. 消费端代码有异常，没有消费成功，异常被mq捕获
3. 消费端返回`*RECONSUME_LATER*`，需要稍后消费



经过查看查看监控报表发现，jvm和os的表现一切正常，所以不存在系统没有消费能力的情况，case1排除。代码中也没有可能发生返回稍后消费的情况，case3排除，所以只能是case2。

那么分析metaQ的日志可以发现下面的情况：

```shell
WARN RocketmqClient - consumeMessage exception: java.util.ConcurrentModificationException, java.util.ArrayList.forEach(ArrarayList.java:1260) 
```

发现系统抛出了`ConcurrentModificationException`这样的并发修改异常，此时基本可以确定是因为多线程访问系统的原因所导致的。而这个异常基本上是和集合的并发修改异常有关的，所以几乎确定了问题的原因。



问题代码如下：

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

### 问题原因

问题就发生在多线程访问list，既做了sort操作，又做了forEach操作，此处会触发list的快速失败机制，源码如下：

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

所谓的快速失败，就是集合会记录查询时候的操作次数，如果在查询时候，被其他线程write，操作次数就会增加，此时系统就会默认有并发问题，抛出`ConcurrentModificationException`



### 解决方案

1. 不能用线程不安全的集合
2. 对于线程不安全的集合来说，不能有即read(如forEach)，又write(如sort)的操作，否则会触发list的快速失败机制
3. 总的来说，对于多线程消费的问题，一定要保证线程安全，即保证公共变量的线程访问是正常的，手段有很多，譬如通过sync，threadLocal，final，等语义来保证



唉，这个快速失败我是知道的，但是，没想到还是踩到这个坑上了。sucks