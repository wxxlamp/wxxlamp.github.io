---
title: "Java并发常见面试题"
tags:
   - Concurrent
   - Java
categories:
   - 面试经验
date: 2019-12-21 10:36
description: "本文整理了Java并发编程的高频面试题，涵盖原子性、有序性、可见性等线程安全基本特性，JMM内存模型与Happens-before规则，ThreadLocal原理与内存泄漏防护，线程池七大参数及任务执行流程，synchronized与ReentrantLock的实现与对比，AQS框架及Semaphore、CountDownLatch、CyclicBarrier等工具类，以及CAS原理、分布式锁实现等核心内容，并附有生产者消费者、顺序打印等实操题。"
---



**珍惜每一天**

> 以下只针对Java岗。来源主要是[牛客](https://www.nowcoder.com/)的Java实习面经。下面的回答直接背就可以，需要一定的Java基础和并发基础，适合春招实习的同学，但是我会在每个问题下把有助于理解的博客贴出来。如果发现有问题欢迎私聊我或留言我会在下面更新

## 基本概念

#### 1. 说下线程安全需要保证的几个基本特性

<!-- more -->

> 阿里19年秋招本科

1. **原子性**：线程是CPU调度的基本单位。CPU有时间片的概念，会根据不同的调度算法进行线程调度。所以在多线程场景下，就会发生原子性问题。因为线程在执行一个读改写操作时，在执行完读改之后，时间片耗完，就会被要求放弃CPU，并等待重新调度。这种情况下，读改写就不是一个原子操作。即存在**原子性问题**。 

   **实现**：`synchronized`其实底层就是使用`monitorenter`和`monitorexit`实现的，在Java中可以使用`synchronized`来保证方法和代码块内的操作是原子性的。 

2. **有序性**：除了引入了时间片以外，由于处理器优化和指令重排等，CPU还可能对输入代码进行乱序执行，比如`load->add->save`有可能被优化成`load->save->add`。这就是**有序性问题**。 

   **实现**：`volatile`关键字会禁止指令重排。`synchronized`关键字保证同一时刻只允许一条线程操作 

3. **可见性**：顾名思义，指当多个线程访问同一个变量时，一个线程修改了这个变量的值，其他线程能够立即看得到修改的值。即本地内存一致性问题(*本地内存指的是虚拟机栈*)。要保证在并发场景下程序运行结果和程序员的预期是一样的。

   **实现**：`volatile`,`synchronized`和`final`三个关键字实现可见性 

这三个基本特性通过JMM来保证.

#### 2. 多线程编程的好处是什么

> 三七互娱19年春招

 充分利用并发

* **从计算机底层来说**， 线程可以比作是轻量级的进程，是程序执行的最小单位,线程间的切换和调度的成本远远小于进程 
* **从当代互联网发展趋势来说**，现在的系统动不动就要求百万级甚至千万级的并发量，而多线程并发编程正是开发高并发系统的基础，利用好多线程机制可以大大提高系统整体的并发能力以及性能
* **对于单核来说**，多线程主要是为了提高 CPU 和 IO 设备的综合利用率
* **对于多核来说:** 多线程主要是为了提高 CPU 利用率 

但是多线程编程也会有弊端： 内存泄漏、上下文切换、死锁以及共享资源的修改值和预期不一样

#### 3. 多线程和单线程的区别

线程是CPU调度和分派的基本单位，多线程编程的目的，就是"**最大限度地利用CPU资源**",当某一线程的处理不需要占用CPU而只和I/O,OEMBIOS等资源打交道时,让需要占用CPU资源的其它线程有机会获得CPU资源，这就是多线程最直观的好处

同时，多线程可发挥多核处理器的优势

还有就是使得建模和编程更加简单

 **一个数据集进行排序，使用单线程还是多线程处理，他们的优劣?**

> 三七互娱19年春招

确定该排序是IO密集型还是计算密集型，如果是IO密集型则多线程，如果是计算密集型则没太大作用。当然，如果是多核CPU的话，一定要是多线程

#### 4. 多进程和多线程的区别

> 网易19年秋招本科

1. 进程间除了IPC通信以外一般不会相互影响；但是一个线程挂掉就会影响整个进程
2. 进程创建销毁比线程复杂
3. 进程之间切换开销大，线程切换简单（对于需要频繁切换的，需要用到多线程）

#### 5. 进程和线程的区别

**不要背书上概念，有实现过吗**

> 滴滴19年秋招，网易19年秋招本科，瓜子二手车19年秋招本科

**进程**是系统进行**资源分配和保护**的基本单位，**线程**是**处理器调度和分派**的基本单位

* 进程具有一个独立的执行环境。 进程是程序在计算机上的一次执行活动 。常情况下，进程拥有一个完整的、私有的基本运行资源集合。特别地，每个进程都有自己的内存空间。进程往往被看作是程序或应用的代名词，然而，用户看到的一个单独的应用程序实际上可能是一组相互协作的进程集合

* 线程有时也被称为轻量级的进程。进程和线程都提供了一个执行环境，但创建一个新的线程比创建一个新的进程需要的资源要少。线程是在进程中存在的，每个进程最少有一个线程。线程共享进程的资源，包括内存和打开的文件

#### 6. 一个线程修改值，另外一个线程能看到修改吗

> 滴滴19年秋招

正常情况下，线程修改的值是工作内存的值，此时别的线程是看不到的。我们可以通过volatile立刻刷新该值到主内存中，这样另外的线程就可以看到值了

对于volatile：

* 读操作时JMM会把工作内存中对应的值设为无效，要求线程从主内存中读取数据
* 写操作时JMM会把工作内存中对应的数据刷新到主内存中，这种情况下，其它线程就可以读取变量的最新值 

#### 7. Happens-before

> 阿里19年秋招

JSR-133规定：

* Happens-before可以理解为一种内存模型，它相对于JMM来说更松散。

* 如果一个动作 happens-before 另一个动作，则第一个对第二个可见，且第一个排在第二个之前。必须强调的是，两个动作之间存在 happens-before 关系并不意味着这些动作 在 Java 中必须以这种顺序发生。happens-before 关系主要用于强调两个有冲突的动作之间的顺序，以及定义数据争用的发生时机

主要有：

* 某个线程中的每个动作都 *happens-before* 该线程中该动作后面的动作
* 某个管程上的 unlock 动作 *happens-before* 同一个管程上后续的 lock 动作
* 对某个 volatile 字段的写操作 *happens-before* 每个后续对该 volatile 字段的读操作
* 在某个线程对象上调用 start()方法 *happens-before* 该启动了的线程中的任意动作
* 某个线程中的所有动作 *happens-before* 任意其它线程成功从该线程对象上的join()中返回
* 如果某个动作 a *happens-before* 动作 b，且 b *happens-before* 动作 c，则有 a  happens-before c
* 对象的构造函数执行的结束 *happens-before* finalize()方法
* 对线程interrupt()方法的调用 *happens-before* 被中断线程的代码检测到中断事件的发生 

[Happens-Before](https://docs.oracle.com/javase/7/docs/api/java/util/concurrent/package-summary.html#MemoryVisibility)

#### 8. JMM内存可见性

> pdd19年实习

JMM通过volatile保证内存可见性

1. 线程终止的时候，工作内存的值会强行刷新到主内存
2. 线程释放锁时，工作内存的值会强行刷新到主内存
3. 使用synchronized和final也可以保证可见性

#### 9. 可见性干了个什么

> 阿里19年秋招

当多个线程访问同一个变量时，一个线程修改了这个变	量的值，其他线程能够立即看得到修改的值

#### 10. 问一下Java的内存模型 

> 阿里19年秋招本科，滴滴19年秋招本科

* JMM是在JSR-133中规定的一系列保证Java正确并发的准则模型，给定一个程序和该程序的一串执行轨迹，*内存模型*描述了该执行轨迹是否是该程序的一次合法执行。内存模型的一个高级、非正式的概述显示其是一组规则，规定了一个线程的写操作何时会对另一个线程可见。表现在Java代码中就是synchronized，volatile，final，JUC等的语义

* 为了保证共享内存的正确性（可见性、有序性、原子性），内存模型定义了共享内存系统中多线程程序读写操作行为的规范。通过这些规则来规范对内存的读写操作，从而保证指令执行的正确性。它与处理器有关、与缓存有关、与并发有关、与编译器也有关。他解决了CPU多级缓存、处理器优化、指令重排等导致的内存访问问题，保证了并发场景下的一致性、原子性和有序性。
* Java内存模型规定了所有的变量都存储在主内存中，每条线程还有自己的工作内存，线程的工作内存中保存了该线程中是用到的变量的主内存副本拷贝，线程对变量的所有操作都必须在工作内存中进行，而不能直接读写主内存。不同的线程之间也无法直接访问对方工作内存中的变量，线程间变量的传递均需要自己的工作内存和主存之间进行数据同步进行。JMM就作用于**工作内存和主存之间数据同步**过程。他规定了如何做数据同步以及什么时候做数据同步

* 内存模型解决并发问题主要采用两种方式：限制处理器优化和使用内存屏障。

#### 11. 多线程如何实现主存同步的

> 滴滴19年本科

一个是JMM可见性

* 线程终止的时候，工作内存的值会强行刷新到主内存
* 线程释放锁时，工作内存的值会强行刷新到主内存
* 使用Volatile也可以保证可见性
* 因为final在初始化完成后具有不变性，这也是JMM可见性的语义

一个是缓存一致性

* MESI
* 总线加#LOCK锁

## Java多线程

#### 1. 线程是不是越多越好，设置数量的考虑

> 京东19年秋招

当然不是越多越好

1. 线程的创建和切换要消耗很多时间和资源（线程池）
2. CPU在线程间频繁的上下文切换也需要消耗时间和资源
3. 每个线程也需要消耗一定的内存空间
4. 服务器CPU核数有限，同时并发的线程数是有限的

公式：
$$
thread_n = (wait_t + compute_t) \div compute_t \times CPU_n
$$

* I/O 密集型为：CPU*2
* 计算密集型为：CPU + 1

#### 2. 多线程是如何控制同步的

> 腾讯19年秋招

通过synchronized，volatile，ThreadLocal，J.U.C来控制同步，下面的问题有详细说明

#### 3. `ThreadLocal`的内部实现

> 头条19年实习，阿里19年秋招

1. `ThreadLocal`提供了线程本地的实例。它与普通变量的区别在于，每个使用该变量的线程都会初始化一个完全独立的实例副本。`ThreadLocal` 变量通常被`private static`修饰。当一个线程结束时，它所使用的所有 `ThreadLocal `相对的实例副本都可被回收。
2. Spring的事物和服务器请求均用到了`ThreadLocal`，总的来说`ThreadLocal`可以非常完美的满足如下两种场景：
   * 每个线程需要有自己单独的实例 *(可通过在线程内部构件一个实例来实现)*
   * 实例需要在多个方法中共享，但不希望被多线程共享 *(可通过`static`或者通过方法间的参数传递来实现)*

3. 每个`Thread`中都存有一个`ThreadLocalMap`字段，它是`ThreadLocal`的内部类，每个线程实例都有自己的`ThreadLocalMap`。`ThreadLocalMap`实例的key为`ThreadLocal`，value为`T`类型的值。在多线程调用中，会存在和线程实例相同的`ThreadLocalMap`，但只有一个`ThreadLocal`。这三者的调用路径为：

$$
Thread\rightarrow ThreadLocal\rightarrow ThreadLocalMap
$$

3. **读取实例**：线程首先通过`getMap((Thread)t)`方法获取自身的`ThreadLocalMap`，然后通过`map.getEntry((TreadLocal)this)`方法获取该`ThreadLocal`在当前线程的`ThreadLocalMap`中对应的`Entry`，最后从`Entry`中取出值即为所需访问的本线程对应的实例。如果`ThreadLocalMap`或者`Entry`为空，则通过 `setInitialValue()`->`createMap(thread,value)`方法设置初始值，此时的`value`则是`initialValue`的返回值。

   *PS：使用`setInitialValue()`而不是`set(T vlaue)`是为了防止用户覆盖`set(T value)`*

4. **设置实例**：除了`initialValue()`初始化的设置实例和私有的`setInitiValue()`，我们主要用`set(T value)`来设置实例。该方法先获取该线程的`ThreadLocalMap`对象，然后直接将`ThreadLocal`对象与目标实例的映射添加进`ThreadLocalMap`中。当然，如果映射已经存在，就直接覆盖。另外，如果获取到的`ThreadLocalMap`为  null，则先创建该`ThreadLocalMap`对象。

5. **防止内存泄漏**：`ThreadLocalMap`的`Entry`对key为`ThreadLocal`的引用为弱引用，避免了`ThreadLocal`对象无法被回收的问题，但是当`ThreadLocal`被回收后为`null`，此时`Entry`无法被GC。所以针对该问题，`ThreadLocalMap`的`set(key, vlaue)`方法中，通过`replaceStaleEntry`方法将所有键为`null`的`Entry`的值设置为`null`从而使得该值可被回收。另外，会在`rehash`方法中通过`expungeStaleEntry`方法将键和值为`null`的`Entry`设置为`null`从而使得该`Entry`可被回收。通过这种方式`ThreadLocal`可防止内存泄漏。 

参考文章：[正确理解Thread Local的原理与使用场景](http://www.jasongj.com/java/threadlocal/)、[JDK1.8 source code](https://docs.oracle.com/javase/8/docs/api/)

#### 4. 线程之间的交互方式有哪些？有没有线程交互的封装类

> 华为19年社招

1. 通过`notify()`/`notifyAll()`：唤醒在此对象监视器锁上被block的（所有）线程，之后再次竞争锁
2. 通过`join()`：A线程执行b.join，那么A线程等待，b线程先执行。该方法通过`wait()`实现
3. 通过`interrupt()`：将调用该方法的线程置为中断状态，通过`isInterrupt()`这个标记来退出此线程
4. 通过`yield()`：使当前线程从执行状态（运行状态）变为可执行态（就绪状态）。CPU会从众多的可执行态里选择，也就是说，当前也就是刚刚的那个线程还是有可能会被再次执行到的，并不是说一定会执行其他线程而该线程在下一次中不会执行到了
5. 线程通过`wait()`和`sleep()`睡眠（这两个方法的作用只是大概一样），然后CPU去调度其他线程

线程交互封装类：不懂

#### 5. 谈谈线程的基本状态，`wait`,`sleep`,`yield`方法的区别

> 华为19年社招

线程共有六种基本状态，分别是`NEW`，`RUNNABLE`，`BLOCKED`，`WAITING`，`TIMED_WAITING`，`TERMINATED`

* `NEW`：线程被new出来，但是没有调用start方法
* `RUNNABLE`：分为运行态和就绪态。就绪态即在等待一些资源如CPU
* `BLOCKED`：等待monitor的锁，一般是要进入`synchronized`块或者方法中的线程。这对应着`synchronized`中对象的`MonitorObject`的`_EntryList`队列
* `WAITING`：当线程调用了`Object.wait()`,`Thread.join()`或者`LockSupport.park()`方法时，进入等待状态，直到使用`notify()`/`notifyAll()`,`LockSupport.unpark()`或者调用方法的线程结束
* `TIMED_WAITING`：是一种特殊的等待状态，当线程调用了`Thread.sleep(long)`,`Object.wait(long)`, `Thread.join(long)`, `LockSupport.parkNanos(long)`或者`LockSupport.parkUntil(long)`方法时，进入超时等待状态
* `TERMINATED`：线程已经完成执行，进入结束状态

`Object.wait()`和`Thread.sleep()`，都可以让线程进入阻塞状态

1. `sleep()`方法使执行中的线程主动让出CPU，进入`TIMED_WAITING`状态，但是不会释放对象锁，在sleep指定时间后CPU便会到可执行状态`RUNNABLE`。注意，runnable并不表示线程一定可以获得CPU。需要等待被CPU调度后进入运行
2. `wait()`方法使执行中的线程主动让出CPU，会**放弃对象锁**，进入`WAITING`状态，只有调用了`notify()` /`notifyAll()`方法，才会从等待队列中被移出，重新获取锁之后，便可再次变成可执行状态(runnable)。 sleep()方法可以在任何地方使用；wait()方法则只能在同步方法或同步块中使用。同时，wait和notify组成经典的等待唤醒机制才是有意义的，单独使用作用不大。wait(long)是没有通知超时返回的方法，此方法单独使用，和sleep效果一样
3. `yield()`方法使当前线程从执行状态（运行状态）变为可执行态（就绪状态），总体上来说该线程一直是在`RUNNABLE`状态。CPU会从众多的可执行态里选择，也就是说，当前也就是刚刚的那个线程还是有可能会被再次执行到的，并不是说一定会执行其他线程而该线程在下一次中不会执行到了

#### 6. Java实现线程同步有哪些方式

> bigo19年秋招本科

线程同步就是两个或两个以上的线程在运行过程中协同步调，按预定的先后次序运行。比如 A 任务的运行依赖于 B 任务产生的数据。如消费者线程需要依靠生产者线程生产消息后，消费者线程才能消费消息

1. 实现线程同步需要锁，一般有两种锁
   * synchronized+wait/notify
   * ReentrantLock+Condition
2. 或者采用Semaphore

#### 7. 创建线程的各种方式

1. 继承`Thread`
2. 实现`Runnable`
3. 通过`FutureTask`和`Callable`
4. 通过线程池

## 线程池

#### 1. 线程池的概念，好处在哪

> 网易19年秋招本科

线程池是池化技术的一种应用，包括数据库连接池，HTTP连接池都是利用了线程池技术。**线程池**提供了一种限制和管理资源（包括执行一个任务）。每个**线程池**还维护一些基本统计信息，例如已完成任务的数量。 

- **降低资源消耗**。通过重复利用已创建的线程降低线程创建和销毁造成的消耗。
- **提高响应速度**。当任务到达时，任务可以不需要的等到线程创建就能立即执行。
- **提高线程的可管理性**。线程是稀缺资源，如果无限制的创建，不仅会消耗系统资源，还会降低系统的稳定性，使用线程池可以进行统一的分配，调优和监控。

####   2. 线程池种类，拒绝策略，任务执行流程

> 小米19年秋招本科，滴滴19年秋招本科

狭义上来说，线程池的种类是指有`Executors`创建的并且底层都是由`ThreadPoolExecutor`实现的四种线程，分别是：

1. `newFixedThreadPool(int nThread)`： 被称为可重用固定线程数的线程池。采用 `ThreadPoolExecutor(nThread,nThread,0L,TimeUnit.MILLISECONDS,new LinkedBlockingQueue<Runnable>());` 从这里我们可以看出来线程池的核心线程和最大线程数是相同的。同时当任务超过线程数时，其等待队列是无限长的(`INTEGER.MAX_VALUE`)，此时当任务过多时会产生内存溢出。**适用于任务量比较固定但耗时长的任务**


2. `newSingleThreadExecutor`：采用 `new FinalizableDelegatedExecutorService    (new ThreadPoolExecutor(1, 1, 0L, TimeUnit.MILLISECONDS, new LinkedBlockingQueue<Runnable>()) );` 可以看出来，核心线程和最大线程数都是1，同时等待队列也是无限长的。至于`FinalizableDlegatedExecutorService()`，它继承了一个关于`ExecutorService`的wrapper类，被包装之后只能调用`ExecutorService`的方法，但是调用不了`ThreadPoolExecutor`类的方法。**适用于一个任务一个任务执行的场景**

3. `newCacheThreadPool`：采用 `new ThreadPoolExecutor(0, Integer.MAX_VALUE, 60L, TimeUnit.SECONDS, new SynchronousQueue<Runnable>(), threadFactory);` 可以看出，核心线程是0，最大线程是`MAX_VALUE`，`KeepAlive`是60s，线程采用的队列是同步队列。当有新任务到来，则插入到`SynchronousQueue`中，由于`SynchronousQueue`是同步队列，因此会在池中寻找可用线程来执行，若有可以线程则执行，若没有可用线程则创建一个线程来执行该任务；若池中线程空闲时间超过60s，则该线程会被销毁。**适用于执行很多短期异步的小程序或者负载较轻的服务器**

4. `newScheduledThreadPool`: 采用`new ThreadPoolExecutor(corePoolSize, Integer.MAX_VALUE, 0, NANOSECONDS, new DelayedWorkQueue());` 可以看出，最大线程为`Integer.MAX_VALUE`，存活时间无限制。等待队列为`DelayedWorkQueue`，是`ScheduledThreadPoolExecutor`的内部类，它是一种按照超时时间排序的队列结构，由堆实现。当运行的线程数没有达到`corePoolSize`的时候，就新建线程去`DelayedWorkQueue`中取`ScheduledFutureTask`然后才去执行任务，否则就把任务添加到`DelayedWorkQueue`，`DelayedWorkQueue`会将任务排序，按新建一个非核心线程顺序执行，执行完线程就回收，然后循环。任务队列采用的`DelayedWorkQueue`是个无界的队列，延时执行队列任务。**适用于执行定时任务和具体固定周期的重复任务**

但其实还有第五种：`newWorkStealingPool`： 创建一个拥有多个任务队列的线程池，可以减少连接数，创建当前可用cpu数量的线程来并行执行，**适用于大耗时的操作，可以并行来执行** 

**线程池的拒绝状态** 一般有四种，分别是1. 丢弃任务并抛出`RejectedExecutionException`异常；2. 也是丢弃任务，但是不抛出异常；3. 丢弃队列最前面的任务，然后重新尝试执行任务（重复此过程）；4. 由调用线程处理该任务

**任务执行流程**

> 阿里19年实习，字节跳动19年秋招本科

整个流程为：
$$
execute() \rightarrow addWorker()\rightarrow Thread.start() \rightarrow runWorker() \rightarrow getTask() \rightarrow processWorkerExit()
$$
四种线程池都是通过`ThreadPoolExecutor`的构造方法实现的，执行任务流程主要是说的该类下的主要方法的具体原理：

* `ThreadPoolExecutor`类中有一个`AtomicInteger`类型的`final`变量`ctl`，该变量有两重意思，一个是表示工作的线程数，另一个是表示当前线程池的五种状态。其实`Integer`类型，共32位，高3位保存runState，低29位保存workerCount 

* 对于`execute(Runnable)`来说：
  * 整体过程是：先提交任务，如果`workerCount`<`corePoolSize`，则新建线程并执行该任务；如果` workerCount` >= `corePoolSize` &&`阻塞队列未满`，则把任务添加到阻塞队列中；如果`workerCount` >= `corePoolSize` && `workerCount` < `maximumPoolSize `&&`阻塞队列已满`，则创建线程并执行该任务；如果 `workerCount` >=  `maximumPoolSize`，则拒绝该任务
  * 从源码上看：首先获得`ctl`的值，如果`workerCount`<`corePoolSize`，则通过`addWorker`提交任务。如果提交任务失败*(有两个原因，一个是线程数超过最大值，另外一个是线程状态不是Running，这也是为何后面要recheck的原因)*，则重新获得`ctl`的值，然后判断线程池的状态，如果为`Running`则把任务插入队列。再次获得`ctl`对线程数目和线程池状态进行`recheck`，如果此时线程池状态不是`Running`则把已经插入队列的任务移出，并调用拒绝策略，如果此时线程池中线程数目为0，则通过`addWorker`新建线程*(此处保证线程池最少有一个线程执行任务)*。之后的情况说明队列已满并且`workCount`>`corePoolSize`，此时再次调用`addWorker`提交任务，提交失败，则拒绝该任务
  
* 对于`addWorker(Runnable,Boolean)`来说，从源码来看，分为3部分：

  * 检查是否`runState`>=`Shutdown`&&(`rs == SHUTDOWN`, `firsTask为空`,`阻塞队列不为空`都成立)，否则返回false
  * 通过CAS增加线程数（并不是实际增加，只是通过增加`ctl`）。其中，`break retry`说明增加成功，`continue retry`说明runState改变，重新开始goto和循环
  * 真正创建新的worker，开始新线程(worker实现了Runnable，也是线程)。创建worker的时候需要通过`ReentrantLock`加锁，创建成功后(`workers.add(worker)`)设置线程池的大小`largestPoolSize`，之后释放锁，然后启动线程，并执行任务


* 对于`Worker`类来说，它是`ThreadPoolExecutor`的内部类，实现了`Runnable`接口，继承了`AQS`，同时线程池底层就是`HashSet<Worker>`这个类

  * 其有两个重要的变量`firstTask`保存了要执行的任务，`thread`通过构造方法中的 `getThreadFactory().newThread(this)`来新建一个线程。所以`t.start()`就等于说调用了`worker.run()`，而`worker.run()`又调用了`worker.runWorker()`方法
  * `Worker`继承自AQS，用于判断线程是否空闲以及是否可以被中断。为什么不用`ReentrantLock`呢？通过`Worker`的`tryAcquire`可以看出该锁是不可重入的，但是`ReentrantLock`却是可重入锁。之所以设置为不可重入锁，主要是不希望当执行譬如`setCorePoolSize()`这样的线程池控制方法时中断正在执行任务的线程*(这种线程池控制方法还有shutdown()等，会调用interruptIdleWorkers()方法来中断空闲的线程，interruptIdleWorkers()方法会使用tryLock()方法来判断线程池中的线程是否是空闲状态，而tryLock()又会通过tryAcquire()来判断线程池中的线程是否是空闲状态。查看源码可得用到了AQS的方法，这也能解释为什么构造方法将state设为-1，即为了禁止在执行任务前对线程进行中断  )*，然后重新获取锁。如果该线程现在不是独占锁的状态，也就是空闲的状态，说明它没有在处理任务，这时可以对该线程进行中断
* 对于`runWorker()`来说：

  * 先通过while循环不断通过`getTask()`去获得任务
  * 如果线程池正在停止，那么要保证当前线程是中断状态，否则要保证当前线程不是中断状态
  * 调用`task.run()`执行任务
  * 如果task为null则跳出循环，执行`processWorkerExit()`方法
  * `runWorker`方法执行完毕，也代表着Worker中的`run`方法执行完毕，销毁线程
  * 注意两个钩子`beforeExecute()`和`afterExecute()`，这两个类是空的，留给子类实现
* 对于`getTask()`来说，它从阻塞队列中获取任务。通过workQueue.poll和take来获取任务，前者是如果在keepAliveTime时间内没有获取到任务，则返回null，后者是一直阻塞直到获取任务
* 而最后一步`processWorkerExit()` 为垂死的Worker做清理和记录。仅从工作线程调用。除非`completedAbruptly`被设置，否则假定workerCount已经被调整以考虑退出。此方法从工作集中移除线程，如果线程因用户任务异常而退出，或者运行的工作线程小于corePoolSize，或者队列非空但没有工作线程，则可能终止池或替换工作线程 

[线程池原理](https://www.cnblogs.com/warehouse/p/10720781.html)

#### 4. 线程池的工作原理，核心线程数和最大线程数什么时候用到 

> 阿里19年秋招

整个线程池通过`ThreadPoolExecutor`类中的一系列方法调用：
$$
execute() \rightarrow addWorker()\rightarrow Thread.start() \rightarrow runWorker() \rightarrow getTask() \rightarrow processWorkerExit()
$$
当新增一个任务时，会先观察是否小于核心线程数，如果小于核心线程数，则直接执行`addWorker()`方法，大于核心线程数且阻塞队列已满，并且当前线程小于最大线程数，则添加该任务并执行。

#### 5. 线程池中的各种接口

> 三七互娱19年春招

从`executor`到`executorService`,`ThreadPoolExecutor`,`Executors`,谈到了里面都有哪些方法？ 

1. 接口`Executor`： 它是一个顶层接口，在它里面只声明了一个方法`void execute(Runnable)`，从字面意思可以理解，就是用来执行传进去的任务
2. 继承1的接口`ExecutorService`：提供了管理终止的方法，以及可为跟踪一个或多个异步任务执行状况而生成 `Future`的方法。增加了`shutDown()`，`shutDownNow()`，`invokeAll()`，`invokeAny()`和`submit()`等方法。如果需要支持即时关闭，也就是`shutDownNow()` 方法，则任务需要正确处理中断 实现了2的抽象类`AbstractExecutorService`：对2的一些主要方法进行了实现，但是没有实现`execute`
4. 继承了3的类`ThreadPoolExecutor`：该类有四种构造线程池的构造方法，线程池主要就说的是这个类
5. 继承了4的类`ScheduledThreadPoolExecutor`：它实现了同样实现了`ExecutorService`接口的`ScheduledExecutorService`接口。该接口增加了`schedule`方法。调用`schedule`方法可以在指定的延时后执行一个`Runnable`或者`Callable`任务。`ScheduledExecutorService`接口还定义了按照指定时间间隔定期执行任务的`scheduleAtFixedRate()`方法和`scheduleWithFixedDelay()`方法 
6. 类`Executors`：线程池中的工具类。该类中有四种构造线程池的方法，使用的是`ThreadPoolExecutor`的四种构造方法

**`ThreadPoolExecutor`的具体工作流程**
$$
execute() \rightarrow addWorker()\rightarrow Thread.start() \rightarrow runWorker() \rightarrow getTask() \rightarrow processWorkerExit()
$$

#### 6. 线程池的参数怎么设置

设置线程池一般会通过`Executors`或者`ThreadPoolExecutor`，但是最终都调用了下面这个方法来设置线程池：

```java
public ThreadPoolExecutor(int corePoolSize, int maximumPoolSize, long keepAliveTime, TimeUnit unit, BlockingQueue<Runnable> workQueue, ThreadFactory threadFactory, RejectedExecutionHandler handler) 
```

其中有7个参数，分别是

1. `corePoolSize`：核心线程数。在创建了线程池后，默认情况下，线程池中并没有任何线程，而是等待有任务到来才创建线程去执行任务，除非调用了`prestartAllCoreThreads()`或者`prestartCoreThread()`方法，在没有任务到来之前就创建`corePoolSize`个线程或者一个线程。当线程数小于核心线程数时，即使现有的线程空闲，线程池也会优先创建新线程来处理任务，而不是直接交给现有的线程处理。核心线程在`allowCoreThreadTimeout`被设置为true时会超时退出，默认情况下不会退出
2. `maximumPoolSize`：最大线程池数。即当需要的线程数超过核心线程数并且任务等待队列已满时，此时线程池可以再创建一批线程来满足需求。但是创建后线程池中的线程数不能超过`maximumPoolSize`

当然也可以在创建完线程池之后通过`setCorePoolSize()`/`setMaximumPoolSize()`修改这些值

3. `keepAliveTime`：当线程空闲时间达到`keepAliveTime`，该线程会退出，直到线程数量等于`corePoolSize`。如果`allowCoreThreadTimeout`设置为true，则所有线程均会退出直到线程数量为0
4. `unit`：`keepAliveTime`的单位，有7种属性，分别是：`DAYS`,`HOURS`,`MINUTES`,`SECONDS`, `MILLISECONDS`, `MICROSECONDS`,`NANOSECONDS`

5. `workQueue`：任务缓存队列及排队策略。当任务超过`maximumPoolSize`后，回到`workQueue`中等待，它有如下三种取值：
   * `ArrayBlockingQueue`：基于数组的先进先出队列，此队列创建时必须指定大小
   * `LinkedBlockingQueue`：基于链表的先进先出队列，如果创建时没有指定此队列大小，则默认为`Integer.MAX_VALUE`
   * `synchronousQueue`：这个队列比较特殊，它不会保存提交的任务，而是将直接新建一个线程来执行新来的任务
6. `threadFactory`：创建线程的工厂，这里可以统一创建线程以及规定线程的属性。推荐使用guava包
7. `handler`：任务拒绝策略。 当线程池的任务缓存队列已满并且线程池中的线程数目达到`maximumPoolSize`，如果还有任务到来就会采取任务拒绝策略，通常有以下四种策略 ：
   * `ThreadPoolExecutor.AbortPolicy`:丢弃任务并抛出`RejectedExecutionException`异常
   * `ThreadPoolExecutor.DiscardPolicy`：也是丢弃任务，但是不抛出异常
   * `ThreadPoolExecutor.DiscardOldestPolicy`：丢弃队列最前面的任务，然后重新尝试执行任务（重复此过程）
   * `ThreadPoolExecutor.CallerRunsPolicy`：由调用线程处理该任务.。因此这种策略会降低对于新任务提交速度，影响程序的整体性能。另外，这个策略喜欢增加队列容量。如果您的应用程序可以承受此延迟并且你**不能任务丢弃任何一个任务请求的话**，你可以选择这个策略。 

**参数设置**

* `corePoolSize`：
  $$
  task_n * task_t
  $$

* `queue`：
  $$
  corePoolSize_n \div task_t \times response_t
  $$

**如果请求超过了线程池的线程数会发生什么**

> 腾讯19年秋招，滴滴19年秋招本科

* 当请求超过了线程池的核心线程数但不超过最大线程时时，会先检查请求队列是否满载，如果请求队列已满，则创建新的线程，如果不满，则把该任务加入请求队列

* 当请求线程超过最大线程时，则采用拒绝策略拒绝该任务

#### 7. 线程池有几种

> oppo19年秋招本科

常见的线程池有四种，分别是：

* `newSingleThreadExecutor()`：只有一个线程处理，等待队列无限大，任务过多容易OOM，适合一个任务一个任务执行的场景
* `newCachedThreadPool()`：核心线程为0，最大线程数无限大，当线程过多时，容易OOM，适合执行很多短期异步的小程序
* `newFixedThreadExecutor()`：核心线程数和最大线程数相同，等待队列无限大，任务过多容易OOM，适合稳定数目的任务
* `newScheduledThreadPool()`：和其他三种有些不一样，继承了`ScheduledThreadPoolExecutor`，同时使用`DelayQueue`，该队列可以按时间远近进行排序。最大线程无限大，当线程过多时，容易OOM，适合做一些固定周期的任务

**说一下线程池的几个重要的参数**

`corePoolSize`,`maxmumPoolSize`,`keepAliveTime`,`unit`,`workQueue`,`threadFactory`,`handle`

**`newFixedThreadPool`这个线程池的初始化大小是怎么决定的**

* I\O密集，2*CPU
* 计算密集：CPU+1
* 公式：（等待时间+计算时间）/计算时间 * CPU

#### ScheduleThreadPool和Timer的区别

1. Timer单线程，不能抛出异常，对系统时间敏感
2. ScheduleThreadPool多线程，能抛出异常，相对时间

[ScheduleThreadPool精讲](http://www.ideabuffer.cn/2017/04/14/%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Java%E7%BA%BF%E7%A8%8B%E6%B1%A0%EF%BC%9AScheduledThreadPoolExecutor/)

#### 8. 自定义的线程池的实现 

> 瓜子二手车19年秋招本科

此处可以继承`ThreadPoolExecutor`，实现一个自定义的线程。实际考察的还是线程池的原理。我们需要知道，线程池中线程的复用主要是在`runWorker()`方法中的`while (task != null || (task = getTask()) != null)`循环决定

具体可以参考我的[Github](https://github.com/stalern/MyConcurrent)

#### 9. SynchronousQueue到底可以存几个

> 滴滴19年秋招本科

因为它是一种同步队列，所以内部没有任何容量。仅在试图要取得元素时，该元素才存在。所以只能存一个

## Java中的锁

#### 1. 说一下死锁，写出来

> 小米19年秋招本科，联行科技19年秋招本科

死锁是指两个或两个以上的进程（或线程）在执行过程中，由于竞争资源或者由于彼此通信而造成的一种阻塞的现象，若无外力作用，它们都将无法推进下去。此时称系统处于死锁状态或系统产生了死锁，这些永远在互相等待的进程称为死锁进程

```java
String s1 = "left";
String s2 = "right";
new Thread(()->{
    while (true){
        synchronized (s1){
            System.out.println("1 get " + s1 + " wait " + s2);
            synchronized (s2){
                System.out.println("1 get " + s2 + " eat");
            }
        }
    }
}).start();

new Thread(()->{
    while (true){
        synchronized (s2){
            System.out.println("2 get " + s2 + " wait " + s1);
            synchronized (s1){
                System.out.println("2 get " + s1 + " eat");
            }
        }
    }
}).start();
```

#### 2. 锁用过没

> 滴滴19年秋招本科

我们常说的锁有两种，一种是synchronized，另一种是ReentrantLock

**锁的什么方法你用过**

* lock：通过acquire加锁

- getHoldCount：获得当前线程重入锁的次数，如果没有则为0

**lock和tryLock区别**

- lock是调用了`acquire()`可以加公平锁，也可以加非公平锁，但是tryLock的无参方法只能加非公平锁
- 对tryLock(arg, nanosTimeOut)来说，如果在给定的等待时间内没有被其他线程持有，并且当前线程没有被中断，则获取锁。 它通过`acquire()`实现，既可以是公平锁，也可以是非公平锁

**ReenTrantLock的公平锁和非公平锁的怎么实现的（源码级别），不限于概念**

公平锁比非公平锁在获取时加了一个判断条件，就是只有当该node节点前面没有节点或者该队列是空队列的时候才加锁

#### 3. Java里怎么实现缓存一致性的

> 滴滴19年秋招本科

volatile、synchronized、lock、信号量、wait/notify

面试官补充：信号量也是加锁实现的

#### 4. jvm的锁优化有什么

> 滴滴19年秋招本科

对于synchronized来说，在JDK1.6之后，优化了相当一部分内容，其中有自旋锁，锁消除，偏向锁，锁粗化，

* 偏向锁：**经过研究发现，大多数情况下，锁不仅不存在多线程竞争，而且总是由同一线程多次获得，为了让线程获得锁的代价更低而引入了偏向锁。**当一个线程访问同步块并获取锁时，会在**对象头和栈帧中的锁记录里存储偏向的线程ID**，以后该线程在**进入和退出同步块时不需要进行 CAS 操作来加锁和解锁**，只需简单的测试一下对象头的 Mark Word 里是否存储着指向当前线程的偏向锁。测试成功则获得该锁，失败会去检查MarkWord中**偏向锁的标志**。如果标志为0，则用CAS竞争锁。如果设置为1，即当前是偏向锁， 则尝试使用 CAS 将对象头的偏向锁指向当前线程。
* 轻量级锁：偏向锁膨胀为轻量级锁之后，线程尝试使用 CAS 将对象头中的 Mark Word 替换为指向锁记录的指针。如果成功，当前线程获得锁，如果失败表示其他线程竞争锁，当前线程便尝试使用自旋来获取锁，当自旋达到一定次数之后未获得锁，便会膨胀成重量级锁。
* 适应性自旋锁：线程加锁的时间一般都很短，所以下一个需要获得锁的线程等一下在阻塞，这个等一下的过程就叫自旋。这种优化方法叫自旋锁。而所谓的自适应自旋锁就是说线程等待的时间不是固定的。自旋锁在1.4就有，只不过默认的是关闭的，jdk1.6是默认开启的

**那还有其他编译器的锁优化吗，比如锁粗化**

同时还有锁粗化和轻量级锁
* 锁粗化：JIT优化，防止对同一个对象连续加锁和解锁。增大了锁的粒度
* 锁消除：JIT通过逃逸分析技术来判断同步块所使用的锁对象是否只能够被一个线程访问而没有被发布到其他线程。 如果是，则消除synchronized，即不用加锁

#### 5. volatile关键字的两层语义

> 阿里19年秋招本科

一层是可以防止重排序，保证了有序性；另外一层是能够立刻把工作内存的值刷新到主内存，并把其他线程的工作内存的值置为无效，保证了可见性

**它的底层原理是啥呢**

对于可见性来说volatile通过加lock锁保证了

- read、load、use动作必须**连续出现**。(把变量从主内存读到工作内存，把工作内存的值放入变量副本中，把变量副本的值传给执行引擎)
- assign、store、write动作必须**连续出现**。(把执行引擎的值赋值给工作内存的变量副本，把工作内存的变量传到主内存中，把主内存的值放入变量中)

对于有序性来说，编译器在生成字节码时，会在指令序列中插入**内存屏障**来禁止特定类型的处理器重排序。然而，对于编译器来说，发现一个最优布置来最小化插入屏障的总数几乎不可能，为此，Java内存模型采取保守策略

* 在每个volatile写操作的前面插入一个StoreStore屏障
* 在每个volatile写操作的后面插入一个StoreLoad屏障
* 在每个volatile读操作的前面插入一个LoadLoad屏障
* 在每个volatile读操作的后面插入一个LoadStore屏障

#### 6. volatile的内部原理

> 三七互娱19年春招，华为19年社招，小米19年秋招本科，京东19年秋招本科

JMM内存模型，冲刷线程中的缓存

参考第五题

#### 7. volatile的具体使用场景 

> 三七互娱19年春招

总的来说有两种：

1. 对变量的写操作不依赖于当前值（i++）
2. 该变量没有包含在具有其他变量的不变式中（setUp，setLow）

具体场景如下：

1. Boolean类型的状态标志（可见性）
2. 一次性安全发布（单例模式，有序性）
3. 独立观察对象的发布
4. JavaBean

[具体使用场景](https://blog.csdn.net/mbmispig/article/details/79255959)

#### 8. Java中的锁如何实现的

> 阿里19年秋招

参看第16题

#### 9. 有什么能保证可见性

> pdd19年实习，京东19年秋招本科

有三种办法，第一种是加锁，即synchronized和ReentrantLock，第二种是volatile，最后一种是final

1. 被synchronized修饰的代码，在开始执行时会加锁，执行完成后会进行解锁。而为了保证可见性，有一条规则是这样的：对一个变量解锁**之前**，必须先把此变量同步回主存中。这样解锁后，后续线程就可以访问到被修改后的值
2. 而ReentrantLock则是通过volatile来实现可见性的，因为lock和unlock是通过volatile修饰的state来实现的，因为state具有可见性，根据happens-before的传递性，在lock到unlock之间的代码也是可见的
3. 对于volatile来说，被volatile修饰的属性能够立刻把工作内存的值刷新到主内存，并把其他线程的工作内存的值置为无效，保证了可见性
4. 对于final来说，被final修饰的字段在构造器中一旦初始化完成，并且没有this逃逸，那在其他线程中就能看见final字段的值。因为final是不可变的，所以满足可见性

#### 10. sync的内部实现，以及优化

> 头条19年实习，小米19年秋招本科，字节跳动19年秋招本科

对于修饰方法来说，会在字节码的flags中表明为ACC_SYNCHRONIZED标识，该标识指明了该方法是一个同步方法，JVM 通过该 ACC_SYNCHRONIZED 访问标志来辨别一个方法是否声明为同步方法，如果有设置，则需要先获得监视器锁，然后开始执行方法，方法执行之后再释放监视器锁。这时如果其他线程来请求执行方法，会因为无法获得监视器锁而被阻断住。值得注意的是，如果在方法执行过程中，发生了异常，并且方法内部并没有处理该异常，那么在异常被抛到方法外面之前监视器锁会被自动释放

当修饰代码块时，会在字节码中通过 `monitorenter` 和 `monitorexit` 执行来进行加锁。当线程执行到 `monitorenter` 的时候要先获得所锁，才能执行后面的方法。当线程执行到 `monitorexit` 的时候则要释放锁。每个对象自身维护这一个被加锁次数的计数器，当计数器数字为 0 时表示可以被任意线程获得锁。当计数器不为 0 时，只有获得锁的线程才能再次获得锁。即可重入锁。

**jvm接收到monitorenter的时候，会执行什么操作**

之后会调用`ObjectMonitor`的`enter`方法，解锁的时候会调用`exit`方法。`ObjectMonitor`是Monitor的实现，有三个主要数据结构

> _owner：指向持有ObjectMonitor对象的线程
>
> _WaitSet：存放处于wait状态的线程队列
>
> _EntryList：存放处于等待锁block状态的线程队列
>
>  _recursions：锁的重入次数 

#### 11. synchronized优化过程 jdk1.6后 jvm层面

> 阿里19年秋招

参见第四题

#### 12. synchronized标注不同的方法有什么区别

> 头条19年实习

静态方法使用的是类锁，普通方法使用的是对象锁

#### 13. synchronized不同使用 区别 

> 阿里19年秋招

synchronized可以同步代码块和方法。同步代码块时使用的是对象锁或类锁。同步静态方法时使用的是类锁，普通方法使用的是对象锁

#### 14. Lock如何给线程分配锁的

> 滴滴19年秋招本科

对于ReentrantLock来说，当调用lock方法时，会先判断state是否为0，如果为0，则通过CAS设置为1，并使得当前线程独占该锁，否则则通过acquire(1)方法去加锁。对于非公平锁来说，会调用`nonfairTryAcquire()`，对于非公平锁来说，会调用`tryAcquire()`。如果获得不到锁，则会将线程放入AQS的队列的队尾，并一直自旋尝试获得锁*(当然，如果前一个节点是SIGNAL，则阻塞当前线程，然后返回线程的中断状态并复位中断状态 ，这是为了防止一直自旋进而耗费CPU资源)*。如果整个过程异常，则取消该节点 

#### 15. synchronized和ReentrantLock的区别 

> 三七互娱19年春招
>
> 先说到了自旋锁，锁消除和锁粗化。最后扯到了Unsafe类就谈不下去了

* 都是可重入锁
* synchronized是Java内置特性，而ReentrantLock是通过Java代码实现的
* synchronized是可以自动获取/释放锁的，但是ReentrantLock需要手动获取/释放锁
* ReentrantLock还具有响应中断、超时等待、中断等待等特性
* ReentrantLock可以实现公平锁，而synchronized只是非公平锁
*  synchronized关键字与`wait()`和`notify()/notifyAll()`方法相结合可以实现等待/通知机制，ReentrantLock类需要借助于`Condition`接口与`newCondition() `方法。实现多路通知功能也就是在一个Lock对象中可以创建多个Condition实例（即对象监视器）。线程对象可以注册在指定的Condition中，从而可以有选择性的进行线程通知，在调度线程上更加灵活。 在使用notify() / notifyAll()方法进行通知时，被通知的线程是由 JVM  选择的，用ReentrantLock类结合Condition实例可以实现“选择性通知“。而synchronized关键字就相当于整个Lock对象中只有一个Condition实例，所有的线程都注册在它一个身上。如果执行notifyAll()方法的话就会通知所有处于等待状态的线程这样会造成很大的效率问题，而Condition实例的signalAll()方法 只会唤醒注册在该Condition实例中的所有等待线程
*  synchronized除了在流程走完释放锁，还在发生异常时，会自动释放线程占有的锁，因此不会导致死锁现象发生；而Lock在发生异常时，如果没有主动通过unLock()去释放锁，则很可能造成死锁现象，因此使用Lock 时需要在finally块中释放锁
* 通过Lock可以知道有没有成功获取锁，而synchronized却无法办到

#### 16. synchronized和ReentrantLock的原理

> 三七互娱19年春招
>
> 问到AQS这一层，已经回答不出来了

synchronized的原理参见第10题

对于ReentrantLock来说，它是一种可重入锁，有两种获取锁的模式：公平锁和非公平锁。所以对应有两个内部类，都继承自Sync。而Sync继承自AQS。因此，所谓的ReentrantLock原理不过也是分析一下Sync自己实现的`tryAcquire()`和`tryRelease()`方法罢了

* Sync主要重新实现了`tryRelease()`和`tryAcquire()`*(通过nonfairTryAcquire())*。对于第一个方法来说，会先判断当前线程和持有锁线程是否一样，如果一样并且当前释放是重入锁的最后一个，则把锁的独占线程置为空。之后再通过` unparkSuccessor()`去唤醒队列中的下一个线程。对于第二个方法来说，它的`nonfairTryAcquire()`主要是针对非公平锁，如果当前state为0，即锁中没有线程，则通过CAS去获得该锁，如果state>0，则判断该线程是否和获得锁的线程一样，即是否是重入的
* 对于公平锁的`tryAcquire()`来说，它比非公平锁多了一个`!hasQueuedPredecessors()`的判断，即检查如果**当前线程位于队列的最前面或队列为空**，才会让它获得锁

#### 17. synchronized锁对象和锁类的区别

> 三七互娱19年春招

* 因为每个对象的MarkWord都有一个Monitor标志位，锁对象即通过该监视器锁进行加锁

* 锁类时其实也是锁的该类的class对象

* 主要区别是同一个类的不同对象使用类锁会是同步的

## Java并发包

JUC中一共包含五种，分别是工具类*( CountDownLatch、CyclicBarrier、Semaphore )*，atomic，lock，并发容器和线程池。其中lock包括了AQS和ReentrantLock。同时 Semaphore，ReentrantReadWriteLock，SynchronousQueue，FutureTask也是基于AQS的

#### 1. atomic类的原理？ 聊一聊使用的场景

> 三七互娱19年春招

atomic中一共有四大类，12个类，四种原子更新方式，分别是

* 原子更新基本类型：`AtomicInteger`,`AtomicLong`,`AtomicBoolean`
* 原子更新数组：`AtomicIntegerArray`,`AtomicLongArray`.`AtomicReferenceArray`
* 原子更新引用：`AtomicReference`,`AtomicReferenceFieldUpdater`,`AtomicMarkableReference`*(该类将 boolean 标记与引用关联起来，也可以解决使用 CAS 进行原子更新时可能出现的 ABA 问题 )*
* 原子更新字段：`AtomicIntegerFieldUpdater`,`AtomicLongFieldUpdater`,`AtomicStampedReference`*( 原子更新带有版本号的引用类型。该类将整数值与引用关联起来，可用于原子的更数据和数据的版本号，可以解决使用CAS进行原子更新时，可能出现的ABA问题 )*
* Atomic包里的类基本都是使用Unsafe实现的包装类

因为要保证原子性的，所以在++时加锁可能会更耗费资源，此时通过atomic包来实现绝对是一种明智的选择。即 当对**一个**共享变量的原子操作，使用atomic会方便的多

#### 2. juc看过哪些，说AQS的机制

> 滴滴19年秋招本科，pdd19年实习

JUC中有线程池(Worker基于AQS)，工具类(基于AQS的semaphore,countDownLock等)，并发容器，atomic和locks（AQS，ReentrantLock）

**概念**

对于AQS来说，他是一个用来构建锁和同步器的框架，基于CAS，使用AQS能简单且高效地构造出应用广泛的大量的同步器，比如我们提到的ReentrantLock，Semaphore，其他的诸如ReentrantReadWriteLock，SynchronousQueue，FutureTask等等皆是基于AQS的。当然，我们自己也能利用AQS非常轻松容易地构造出符合我们自己需求的同步器

**使用**

从使用上来说，AQS的功能可以分为两种：独占（如ReentrantLock）和共享（如Semaphore/CountDownLatch CyclicBarrier/ReadWriteLock)。ReentrantReadWriteLock可以看成是组合式，它对读共享，写独占

AQS的设计是基于模板方法模式的，如果需要自定义同步器一般的方式，则需要：

1. 使用者继承AbstractQueuedSynchronizer并重写指定的方法。（这些重写方法很简单，无非是对于共享资源state的获取和释放）

2. 将AQS组合在自定义同步组件的实现中，并调用其模板方法，而这些模板方法会调用使用者重写的方法

   ```java
   isHeldExclusively()//该线程是否正在独占资源。只有用到condition才需要去实现它。
   tryAcquire(int)//独占方式。尝试获取资源，成功则返回true，失败则返回false。
   tryRelease(int)//独占方式。尝试释放资源，成功则返回true，失败则返回false。
   tryAcquireShared(int)//共享方式。尝试获取资源。负数表示失败；0表示成功，但没有剩余可用资源；正数表示成功，且有剩余资源。
   tryReleaseShared(int)//共享方式。尝试释放资源，成功则返回true，失败则返回false。
   ```

    默认情况下，每个方法都抛出 `UnsupportedOperationException` 。为什么不是abstract的呢？如果是abstract则说明每个使用者都要实现这些方法，要求比较苛刻。

**原理**

* AQS维护一个共享资源`state`，它的语义有响应的子类来实现，譬如在`ReentrantLock`中，`state`初始化为0，表示未锁定状态。A线程`lock()`时，会调用`tryAcquire()`独占该锁并将state+1。此后，其他线程再`tryAcquire()`时就会失败，直到A线程`unlock()`到`state`=0（即释放锁）为止，其它线程才有机会获取该锁。在`CountDownLatch`中，任务分为N个子线程去执行，`state也`初始化为N（注意N要与线程个数一致）。这N个子线程是并行执行的，每个子线程执行完后`countDown()`一次，state会CAS减1。等到所有子线程都执行完后(即state=0)，会`unpark()`主调用线程，然后主调用线程就会从await()函数返回，继续后余动作 

* AQS通过内置的FIFO双端双向链表来完成获取资源线程的排队工作，双端双向链表。该队列由一个一个的`Node`结点组成，每个`Node`结点维护一个`prev`引用和`next`引用，分别指向自己的前驱和后继结点。AQS维护两个指针，分别指向队列头部`head`和尾部`tail`。该队列中的`Node`有五种状态，分别是`CANCELLED`,`SIGNAL`, `CONDITION`,`PROPAGATE`和初始状态
  * **CANCELLED**(1)：表示**当前结点**已取消调度。当timeout或被中断（响应中断的情况下），会触发变更为此状态，进入该状态后的结点将不会再变化
  * **SIGNAL**(-1)：表示**后继结点**在等待当前结点唤醒。后继结点入队时，会将前继结点的状态更新为SIGNAL
  * **CONDITION**(-2)：表示结点等待在Condition上，当其他线程调用了Condition的signal()方法后，CONDITION状态的结点将**从等待队列转移到同步队列中**，等待获取同步锁
  * **PROPAGATE**(-3)：共享模式下，前继结点不仅会唤醒其后继结点，同时也可能会唤醒后继的后继结点
  * **0**：新结点入队时的默认状态
  
* 当加锁时，子类通过调用AQS的`acquire()`进而调用子类自己实现的`tryAcquire()`方法（该方法是尝试获得锁，即改变state的状态），在调用`tryAcquire()`方法的过程中：先尝试获得锁，如果成功则返回，如果获得不成功则把该线程加入到Node队列中*(节点为空时，自旋创建节点并设置尾点)*，然后自旋尝试获得锁*(只有老二结点，才有机会去tryAcquire，如果不是且当其前驱节点是SINGAL，则阻塞)*，之后返回中断状态

  ```java 
  if (!tryAcquire(arg) 
      && acquireQueued(addWaiter(Node.EXCLUSIVE), arg))            
      selfInterrupt();
  ```
  
* 当释放锁时，和加锁流程一样。当释放成功后则去唤醒后面的节点

  ```JAVA
  public final boolean release(int arg) {
      if (tryRelease(arg)) {
          Node h = head;
          if (h != null && h.waitStatus != 0)
              unparkSuccessor(h);
          return true;
      }
      return false;
  }
  ```

**组件**

除了ReentrantLock外，还有三种常用的AQS组件，分别是`Semaphore`,`CountDownLatch`和`CyclicBarrier`

- **Semaphore(信号量)-允许多个线程同时访问：** synchronized 和 ReentrantLock 都是一次只允许一个线程访问某个资源，Semaphore(信号量)可以指定多个线程同时访问某个资源。(PS:学过OS的应该都知道把)
- **CountDownLatch （倒计时器）：** CountDownLatch是一个同步工具类，用来协调多个线程之间的同步。这个工具通常用来控制线程等待，它可以让某一个线程等待直到倒计时结束，再开始执行。
- **CyclicBarrier(循环栅栏)：** CyclicBarrier 和 CountDownLatch 非常类似，它也可以实现线程间的技术等待，但是它的功能比  CountDownLatch 更加复杂和强大。主要应用场景和 CountDownLatch 类似。CyclicBarrier  的字面意思是可循环使用（Cyclic）的屏障（Barrier）。它要做的事情是，让一组线程到达一个屏障（也可以叫同步点）时被阻塞，直到最后一个线程到达屏障时，屏障才会开门，所有被屏障拦截的线程才会继续干活。CyclicBarrier默认的构造方法是 CyclicBarrier(int parties)，其参数表示屏障拦截的线程数量，每个线程调用await()方法告诉  CyclicBarrier 我已经到达了屏障，**然后当前线程被阻塞**

[深入理解AQS（一）](http://ideabuffer.cn/2017/03/15/%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3AbstractQueuedSynchronizer%EF%BC%88%E4%B8%80%EF%BC%89/)

[Guide](https://snailclimb.gitee.io/javaguide/#/docs/java/Multithread/JavaConcurrencyAdvancedCommonInterviewQuestions?id=_6-aqs)

#### 3. 了解juc？说说juc，举个例子

> 京东19年秋招本科，阿里19年秋招

JUC中有线程池(Worker基于AQS)，工具类(基于AQS的semaphore,countDownLock等)，并发容器，atomic和locks（AQS，ReentrantLock）

对于ConcurrentHashMap来说，因为HashMap 不是线程安全的，在并发场景下如果要保证一种可行的方式是使用 `Collections.synchronizedMap()` 方法来包装我们的 HashMap。但这是通过使用一个全局的锁来同步不同线程间的并发访问，因此会带来不可忽视的性能问题。

所以就有了 HashMap 的线程安全版本—— ConcurrentHashMap 的诞生。在 ConcurrentHashMap  中，无论是读操作还是写操作都能保证很高的性能：在进行读操作时(几乎)不需要加锁，而在写操作时通过锁分段技术只对所操作的段加锁而不影响客户端对其它段的访问

#### 4. atomic下的原子类有用到吗？

> 阿里19年秋招，bigo19年秋招本科

用到了AtomicInteger，底层是用的CAS实现的

AtomicInteger 类主要利用 CAS+ volatile 和 native 方法来保证原子操作，从而避免 synchronized 的高开销，执行效率大为提升

在JDK8中，对于`getAndIncrement()`来说，会直接调用`unsafe.getAndAddInt()`方法，之后会通过两个native方法`getIntVolatile(o, offset)`和`weakCompareAndSetInt()`，第一个方法的作用是从给定偏移量的内存地址获取给定对象o中的字段或数组元素，第二个方法的作用是通过CAS去更新值，CAS的原理是拿期望的值和原本的一个值作比较，如果相同则更新成新的值

#### 5. CAS

**原理，产生问题，如何解决，使用场景**

> 三七互娱19年春招，oppo19年秋招本科，bigo19年秋招本科

1. CAS怎么实现的
   - CAS是在JDK5引进的，通过UnSafe类实现
   - JDK8以前和JDK8（包括8）以后的实现方式略有不同，但总体一样
2. CAS本质性实现原理是什么？
   - CAS的原理是拿期望的值和原本的一个值作比较，如果相同则更新成新的值 
   - 但是可能会出现ABA问题，可以通过版本号机制解决

#### 6. 如何避免CAS一直自旋消耗资源

> 字节跳动19年秋招本科

可以为自旋时间加上限制，如果自旋超过一定时间之后，就将该线程放置为阻塞状态。像AQS中的`acquireQueue`方法就用了这种手段，如果该节点的前置节点是SIGNAL，则阻塞该线程

#### 7. CAS比分段锁好在哪里，缺点又是什么

> 字节跳动19年秋招本科

将数据分为一段一段的存储，然后给每一段数据配一把锁，当一个线程占用锁访问其中一个段数据时，其他段的数据也能被其他线程访问，这就是**分段锁**

不用加锁，效率更高

但是会产生ABA问题，一直自旋会消耗CPU资源

#### 8. CAS算法在哪里有应用？

> 阿里19年秋招

JDK整个JUC包都是基于CAS算法的

#### 9. 讲一下ConcurrentHashMap

> 阿里19年秋招

参看集合面经

#### 10. Hashmap和Concurrenthashmap

> 滴滴19年秋招本科，科大讯飞19年秋招本科，pdd19年实习

这个和集合也密切相关，我集合面经中有说

**各版本的区别**

JDK1.7的 ConcurrentHashMap 底层采用 **分段的数组+链表** 实现

JDK1.8 采用的数据结构跟HashMap1.8的结构一样，数组+链表/红黑二叉树 

## 分布式锁

这个模块我在JavaEE Plus模块中也有细说

#### 1. 分布式锁和锁区别，什么时候用，怎么考虑的

> 京东19年秋招

普通锁针对多线程的场景，一般可以synchronized和lock。而分布式针对的是分布式的环境，系统部署在多个机器中，也会出现并发问题，并且场景是多个进程之间的并发问题。使用内存标记无法解决这个问题，因为内存是线程共享的

分布式锁是防止多进程出现并发问题，所以不可以借助内存来实现锁的功能。但是可以借助redis、memcached（Memcached 是一个高性能的分布式内存对象缓存系统）、zookeeper实现。

#### 2. 分布式锁的实现手段有哪些

> 京东19年秋招

* zookeeper。每个客户端对某个功能加锁时，在zookeeper上的与该功能对应的指定节点的目录下，生成一个唯一的瞬时有序节点。判断是否获取锁的方式很简单，只需要判断有序节点中序号最小的一个。当释放锁的时候，只需将这个瞬时节点删除即可。同时，其可以避免服务宕机导致的锁无法释放，而产生的死锁问题。优点：锁安全性高，zk可持久化。缺点：性能开销比较高。因为其需要动态产生、销毁瞬时节点来实现锁功能
* memcached带有add函数，利用add函数的特性即可实现分布式锁。add和set的区别在于：如果多线程并发set，则每个set都会成功，但最后存储的值以最后的set的线程为准。而add的话则相反，add会添加第一个到达的值，并返回true，后续的添加则都会返回false。利用该点即可很轻松地实现分布式锁。优点：并发高效。缺点：memcached采用列入LRU置换策略，所以如果内存不够，可能导致缓存中的锁信息丢失。memcached无法持久化，一旦重启，将导致信息丢失
* redis可以使用jedis.set实现，并且设置过期时间，否则如果加完锁出现故障就会导致死锁*(redis获取锁的那个客户端bug了或者挂了，那么只能等待超时时间之后才能释放锁)*。redis分布式锁，其实需要自己不断去尝试获取锁，比较消耗性能

## 场景题

#### 1. 当数据正在更新，如何解决不同线程更新一个变量的问题

> 三七互娱19年春招

使用锁或者atomic

#### 2. 怎么获得一个线程安全的list

> 瓜子二手车秋招本科

通过` Collections.synchronizedList(new ArrayList()); `

## 实操题

#### 3. 生产者消费者模型

> 阿里19年秋招，京东19年秋招本科

有多种方式：

* synchronized+wait/notifyAll
* ReentrantLock+Condition
* Semaphore
* PipedInputStream+PipedOutputStream

```java
public class ProAndCon {

    private static final int BUFFER = 1024;
    private static Semaphore empty = new Semaphore(BUFFER);
    private static Semaphore full = new Semaphore(0);
    private static Semaphore mutex = new Semaphore(1);
    private static int in = 1;
    private static int out = 1;

    private static class Producer implements Runnable {

        @Override
        public void run() {
            try {
                empty.acquire();
                mutex.acquire();
                System.out.println("生产" + in);
                in = (in + 1) % BUFFER;
                mutex.release();
                full.release();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
    private static class Consumer implements Runnable {

        @Override
        public void run() {
            try {
                full.acquire();
                mutex.acquire();
                System.out.println("消费" + out);
                out = (out + 1) % BUFFER;
                mutex.release();
                empty.release();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public static void main(String[] args) {
        for (int i = 0; i < 100; i++) {
            new Thread(new Producer()).start();
            new Thread(new Consumer()).start();
        }
    }
}
```

**有什么注意事项**

#### 4. 通过N个线程顺序循环打印从0至100

> 阿里19年秋招本科

如给定N=3则输出：
thread0: 0
thread1: 1
thread2: 2
thread0: 3
thread1: 4
...

```java
public class SeqPrint {
    //工作线程数量
    static final int WORKER_COUNT = 3;
    //是计数器
    static int countIndex = 0;

    public static void main(String[] args){
        final ReentrantLock reentrantLock = new ReentrantLock();
        final List<Condition> conditions = new ArrayList<>();
        for(int i=0; i< WORKER_COUNT; i++){
            Condition condition = reentrantLock.newCondition();
            conditions.add(condition);
            Worker worker = new Worker(i, reentrantLock, conditions);
            worker.start();
        }

        new Thread(() -> {
            reentrantLock.lock();
            try {
                conditions.get(0).signal();
            } finally {
                reentrantLock.unlock();
            }
        }).start();

    }

    static class Worker extends Thread{
        
        int index;
        ReentrantLock lock;
        List<Condition> conditions;

        public Worker(int index, ReentrantLock lock, List<Condition> conditions){
            super("Worker:"+index);
            this.index = index;
            this.lock = lock;
            this.conditions = conditions;
        }

        private void signalNext(){
            int nextIndex = (index + 1) % conditions.size();
            conditions.get(nextIndex).signal();
        }

        @Override
        public void run(){
            while(true) {
                lock.lock();
                try {
                    conditions.get(index).await();
                    if (countIndex > 100) {
                        signalNext();
                        return;
                    }
                    System.out.println((this.getName() + " " + countIndex));
                    countIndex ++;
                    signalNext();
                }catch (Exception e){
                    e.printStackTrace();
                }finally {
                    lock.unlock();
                }
            }
        }
    }
}
```



#### 5. 手写一个计数器，开10个线程,保证最后计数输出为10

> 阿里19年秋招本科

```java
public class Counter {

    private AtomicInteger count;

    public Counter(int value) {
        count = new AtomicInteger(value);
    }
    public boolean add() {
        for (;;){
            long time = System.currentTimeMillis();
            int memory = count.get();
            if (count.compareAndSet(memory, memory + 1)) {
                return true;
            }
            if (System.currentTimeMillis() - time > 10L) {
                return false;
            }
        }
    }

    public int get() {
        return count.get();
    }

    public static void main(String[] args) {
        Counter counter = new Counter(0);
        for (int i = 0; i < 10; i++) {
            counter.add();
        }
        System.out.println(counter.get());
    }
}
```

















 	











[牛客总结](https://www.nowcoder.com/discuss/344311?type=2&order=4&pos=3&page=3)

1. 线程状态，start,run,wait,notify,yield,sleep,join等方法的作用以及区别 
2. wait,notify阻塞唤醒确切过程？在哪阻塞，在哪唤醒？为什么要出现在同步代码块中，为什么要处于while循环中？  
3. 线程中断，守护线程  
4. Java乐观锁机制，CAS思想？缺点？是否原子性？如何保证？  
5. synchronized使用方法？底层实现？  
6. ReenTrantLock使用方法？底层实现？和synchronized区别
7. 公平锁和非公平锁区别？为什么公平锁效率低？  
8. 锁优化。自旋锁、自适应自旋锁、锁消除、锁粗化、偏向锁、轻量级锁、重量级锁解释  
9. Java内存模型  
10. volatile作用？底层实现？禁止重排序的场景？单例模式中volatile的作用？ 
11. AQS思想，以及基于AQS实现的lock, CountDownLatch、CyclicBarrier、Semaphore介绍  
12. 线程池构造函数7大参数，线程处理任务过程，线程拒绝策略  
13. Execuors类实现的几种线程池类型，阿里为啥不让用？ 
14. 线程池大小如何设置？
15. 手写简单的线程池，体现线程复用  
16. 手写消费者生产者模式
17. 手写阻塞队列
18. 手写多线程交替打印ABC



总结：

关键字：synchronized（实现，优化），volatile，final

概念：JMM，happens-before

JUC：线程池，容器(COW)，工具类（借助了AQS），lock（AQS,ReentrantLock,ReadAndWriteLock），atomic