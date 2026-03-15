---
title: "开水团面试"
tags:
   - Java
   - Campus Recruitment
categories:
   - 面试经验
date: 2020-08-20 10:36
description: "美团基础架构部实习面试经验，涵盖HashMap、JVM、MySQL、Redis等Java后端核心知识点。"
---

从公司实习结束后回来的下一周就开始面开水团，部门是基础架构部，进度算是我现在面试流程中最快的一个了。

整体来说难度适中，可以用来练手。

<!-- more -->

### 一面

### Java

#### 1. HashMap和ConcurrentHashMap

HashMap是基于拉链式的散列方法，当阈值超过3/4*cap时，就会进行桶的扩容，扩容时如果红黑树的个数小于6则重新变为链表。扩容的时候会拆分成两个链表（要么一致，要么差一个oldCap）

ConcurrentHashMap有一个特别的字段`sizeCtl`，不同的值有不同的含义。当为负数时：-`1`代表正在初始化，-N代表有N-`1`个线程正在 进行扩容；当为`0`时：代表当时的table还没有被初始化；当为正数时：表示初始化或者下一次进行扩容的大小。Con在计算size的时候有两个步骤，重复计算三次，不一样的话加锁计算

**红黑树的结构**

#### 2. Java9+新特性

- JDK9的jshell，接口私有方法，多版本兼容jar，try-with-resourses的改进，创建不可变集合，增强stream API，把String的char[]改为byte[]
- jdk11支持局部变量类型推导
- jdk12 switch不用写break

#### 3. Jvm的内存结构

堆，方法区，虚拟机栈，本地方法栈和程序计数器

#### 3. 线程池的原理

核心线程，最大线程，等待时间，等待单位，拒绝策略，线程工厂，阻塞队列

**如何衡量线程池比较快**

可以通过Java当中的Timer类来实现

#### 4. sleep和wait

sleep和wait在执行后头处于WAITING或者TIME_WAITING的状态

wait和notify搭配使用，wait是释放锁的

sleep属于Thread，wait属于Object

**wait后处于线程的哪个生命周期**

处于Runnable

### Redis

#### 5. Redis的数据结构

Redis有五种数据类型，分别是list(ziplist,linkedlist)，str(int,raw,embstr)，set(inset,hashtable)，sorted set(ziplist,skiplist)，hash(ziplist,hashtable)



整体来说是一个key和value的形式，每个key和value对象都是由redisObject来保证的(type，encoding，lru)，type指的是五大数据类型，encoding指的是对应着五种数据类型的编码（int，embstr，raw，ht，linkedList，Ziplist，intset，skipList）

### OS

#### 6. 如何排查CPU飙到100

可能会有死锁，while循环，内存溢出和内存泄漏导致的频繁GC

首先通过top查看当前机器的应用所耗的资源

如果是Java应用，则需要通过jstat -gcutil 去查看当前的GC情况

排查堆中异常多的类实例

**如何定位问题代码**

如果是死锁的话，可以通过jstack 来定位死锁代码

### 算法

#### 7. 翻转链表

```java
import java.util.Scanner;
public class Main {
  public static void main(String[] args) {
    Scanner in = new Scanner(System.in);
    int n = in.nextInt();
    ListNode head = new ListNode();
    ListNode node = head;
    for(int i = 0; i < n; i ++) {
      head.val = in.nextInt();
      ListNode temp = new ListNode();
      head.next = temp;
      head = temp;
    }
    ListNode newNode = reverse(node);
    while(newNode != null) {
      System.out.print(newNode.val + " ");
      newNode = newNode.next;
    }

  }
  static class ListNode {
    int val;
    ListNode next;
  }
  private static ListNode reverse(ListNode head) {
    ListNode pre = null, cur = head;
    while(cur != null) {
      ListNode next = cur.next;
      cur.next = pre;
      pre = cur;
      cur = next;
    }
    return pre;
  }
}
```

### 二面

### Java

#### 1. Java线程的状态

哪些状态消耗CPU

哪些方法可以改变状态

#### 2. 哪些对象可以作为GCRoot

栈中引用的对象，静态对象，方法区中常量引用的对象，栈中JNI的对象

#### 3. Jvm的GC

### 网络

#### 4. TCP的一些状态

syn_send, syn_recv, established

fin_wait_1, fin_wait_2, close_wait, time_wait, closed

#### 5. TIMEWAIT的作用

1. 可靠的终止TCP连接
2. 保证让迟来的TCP报文段有足够的时间被识别并丢弃

### DB

#### 6. 数据库的聚簇索引

#### 7. 如何优化数据库

#### 8. 查询成绩第二的同学

**table_score: id name score:**

```sql
SELECT id, name, MAX(score) AS score
FROM table_score
WHERE score < (SELECT MAX(score) FROM table_score); 
```

### 其他

#### 9. 分布式事物解决方案

rocketMQ的事务性消息中，Broker是如何轮询的？



### 算法

删除字符串中的a和bc

```java
private static char[] test(char[] cs) {
  int j = 0;
  for(int i = 0; i < cs.length; i ++) {
    if(cs[i] == 'a') continue;
    if(cs[i] == 'b') {
      int b = 0, c = 0;
      while(cs[i] == 'b' || cs[i] == 'c'){
        if (cs[i] == 'b') b ++;
        else c ++;
        i ++;
      }
      int t = Math.abs(b-c);
      char cr = b > c ? 'b' : 'c';
      while(t-- > 0) cs[j++] = cr;
    } else {
      cs[j ++] = cs[i];
    }
  }
  while(j < cs.length) {
    cs[j ++] = '0';
  }
  return cs;
}
```

#### 三面&HR面



三面和HR有一拼，都没问题技术：

#### 1. 喜欢做什么

技术，业务，兴趣

#### 2. 如何评价自己在实习中的表现

#### 3. 如何学习

#### 4. 如何甄别互联网的糟粕

#### 5. 最近在学什么（非技术）

**如何通过学习驱动自己，以至于形成产出**

#### 6. 自己突破最大的一件事

#### 7. 高考成绩和GPA

#### 8. 对地点的要求