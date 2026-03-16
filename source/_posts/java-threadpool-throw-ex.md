---
title: "当线程池的任务抛出异常..."
tags:
   - Java
   - Concurrent	
categories:
   - 采坑记录
date: 2022-08-09 23:36
description: "本文通过实际踩坑，深入分析Java线程池在execute、submit、schedule三种提交方式下任务抛出异常时的不同行为表现：execute会直接抛出并销毁Worker线程后重建；submit通过FutureTask吞掉异常，需调用get方法才能感知；schedule任务抛异常后不再重新入队导致定时任务静默停止。文章结合ThreadPoolExecutor源码逐一解析原因，并给出任务内捕获异常、设置UncaughtExceptionHandler、显式调用get等解决方案。"
---

最近在应用场景中需要用线程池开多线程，但是有时候通过日志和监控会发现，异步线程的任务突然停止，搞得我排查起来一脸懵逼，无从下手，后来师兄帮我翻业务代码才发现，原来是新线程里的任务抛出运行时异常了，导致我开的用户线程直接“跪”了。那么为什么线程池中的线程不会将异常抛出来呢，抛出异常的线程又会是什么状态呢？此贴特地分析一下

### 情况复现
#### `#submit`

1. 线程执行的任务抛出异常，但是没有被处理
1. 发生业务异常的用户线程并没有“挂掉”，而是变成了`WATTING`
1. 程序还在运行

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/dd569787_java-threadpool-throw-ex-1.png" align="middle" />

#### `#execute`

1. 线程执行的任务抛出异常，被成功捕获
1. 发生业务异常的用户线程直接结束，状态变成了`TERMINATED`
1. 系统没有结束，还在运行

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/72c0a509_java-threadpool-throw-ex-2.png" align="middle" />

#### `#schedule`

1. 线程执行的任务抛出异常，但是没有被处理
1. 线程池中线程的状态为`WATTING`
1. 程序继续运行，但是抛出异常的定时任务不再被执行

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/d41f4b8a_java-threadpool-throw-ex-3.png" align="middle" />

### 原因分析
#### #execute
对于execute来说，这个比较好理解，从源码中可以发现，线程池中的线程在执行`runWorker`的时候，如果任务中抛出异常，则线程会直接将异常抛出：
```java
 final void runWorker(Worker w) {
     // ... 省略代码
     try {
         while (task != null || (task = getTask()) != null) {
             // ... 省略代码
             try {
                 beforeExecute(wt, task);
                 Throwable thrown = null;
                 try {
                     task.run();
                 } catch (RuntimeException x) {
                     thrown = x; throw x; // 这里抛出异常
                 } catch (Error x) {
                     thrown = x; throw x;
                 } catch (Throwable x) {
                     thrown = x; throw new Error(x);
                 } finally {
                     afterExecute(task, thrown);
                 }
             } finally {
                 task = null;
                 w.completedTasks++;
                 w.unlock();
             }
         }
         completedAbruptly = false;
     } finally {
         processWorkerExit(w, completedAbruptly); // 抛出异常后，执行这里
     }
 }
```
并且，在抛出异常后，为了避免异常任务的线程被污染，执行该任务的worker线程会被销毁，然后重新创建一个无任务非核心的worker线程。所以，即使线程池中的所有任务都失败了，只要核心线程数不为0，程序就将会一直被`workQueue#poll`阻塞，导致Jvm不会退出
```java
private void processWorkerExit(Worker w, boolean completedAbruptly) {
    if (completedAbruptly) // If abrupt, then workerCount wasn't adjusted
        decrementWorkerCount();

    final ReentrantLock mainLock = this.mainLock;
    mainLock.lock();
    try {
        completedTaskCount += w.completedTasks;
        workers.remove(w); // 移除当前异常Worker
    } finally {
        mainLock.unlock();
    }

    tryTerminate();

    int c = ctl.get();
    if (runStateLessThan(c, STOP)) { // 如果不是STOP状态
        if (!completedAbruptly) {
            int min = allowCoreThreadTimeOut ? 0 : corePoolSize;
            if (min == 0 && ! workQueue.isEmpty())
                min = 1;
            if (workerCountOf(c) >= min) // 且线程数小于核心线程
                return; 
        }
        addWorker(null, false); // 新增一个线程执行
    }
}
```
#### #submit
对于submit来说，可能要相对特殊一点，因为它执行的任务是有返回值的，在一开始的提交任务的时候，线程池就通过`FutureTask`对其进行了封装
```java
public Future<?> submit(Runnable task) {
    if (task == null) throw new NullPointerException();
    RunnableFuture<Void> ftask = newTaskFor(task, null); // 封装该应用
    execute(ftask);
    return ftask;
}
```
所以，在线程池执行`runWorker`的方法时，实际进入的下面的方法：
```java
public void run() {
    // ... 省略代码
    try {
        Callable<V> c = callable;
        if (c != null && state == NEW) {
            V result;
            boolean ran;
            try {
                result = c.call();
                ran = true;
            } catch (Throwable ex) {
                result = null;
                ran = false;
                setException(ex); // FutureTask会catch异常
            }
            if (ran)
                set(result);
        }
    } finally {
        // ... 省略代码
    }
}
```
这个时候，真相就慢慢浮出水面，`FutureTask`会将异常封装成outcome的Object对象，在使用`FuntureTask#get`调用`report`方法的时候，将异常封装成`ExecutionException`重新抛出：
```java
public V get() throws InterruptedException, ExecutionException {
    int s = state;
    if (s <= COMPLETING)
        s = awaitDone(false, 0L);
    return report(s);
}
private V report(int s) throws ExecutionException {
    Object x = outcome;
    if (s == NORMAL)
        return (V)x;
    if (s >= CANCELLED)
        throw new CancellationException();
    throw new ExecutionException((Throwable)x); // 抛出该异常
}
```
至于此时为啥线程池中的线程还处于`WAITING`状态，则是因为当前任务执行结束，`Worker`在调用`workQueue#poll`方法被阻塞了而已
#### #schedule
`#schedule`是定时线程池的执行方法，按照道理讲，即使任务抛出异常，线程池也应该定时执行该任务，那为什么任务被停止了呢？
这要回到`FutureTask`的子类`ScheduledFutureTask`中去看，我们可以发现，正常情况下，当定时任务被执行完成的时候，线程会重新把该任务放到执行队列中
```java
public void run() {
    boolean periodic = isPeriodic();
    if (!canRunInCurrentRunState(periodic))
        cancel(false);
    else if (!periodic)
        ScheduledFutureTask.super.run();
    else if (ScheduledFutureTask.super.runAndReset()) { 
        setNextRunTime();
        reExecutePeriodic(outerTask);// 重新将任务放到队列中执行
    }
}
```
但是我们深入进`#runAndReset`方法中就会发现，当任务抛出异常，`#runAndReset`返回的是false，此时就不会将定时任务入列了，所以，抛出异常的定时任务，是不会被重新执行的
```java
protected boolean runAndReset() {
    // ...省略代码
    boolean ran = false;
    int s = state;
    try {
        Callable<V> c = callable;
        if (c != null && s == NEW) {
            try {
                c.call(); // don't set result
                ran = true;
            } catch (Throwable ex) {
                setException(ex); // 抛出异常后，ran仍然是false
            }
        }
    } finally {
        // ...省略代码
    }
    return ran && s == NEW; // 此处返回false
}
```
### 解决方案

1. 在任务中捕获异常并处理，防止干扰到线程池线程的执行
1. 如果是`#execute`方法的话，可以利用`ThreadFactory`设置处理线程unCatch异常的逻辑
1. 如果是`#submit`或者是`#schedule`这样通过`Callable`的调用，则需要调用其`#get`方法，对任务的异常进行显示的处理


### 一些思考
这次的问题，只要了解线程池，还是比较简单的；相对来说，比较充分地暴露出来我基础知识不够展示的地方，以前都是背八股文，虽然在背的时候，对线程池的ctl，各种配置张口就来，但是过段时间后，在真正使用，遇见问题时还是一脸懵逼。果然有句话说得好，“看过的，只能是别人的，唯有经历了，才是自己的”～


#### 如何关闭线程
线程池shutdown的时候，就会关闭一些线程，这个是如何做的呢？
当调用线程池的`#shutdown`方法的时候，线程池会遍历所有的workers，然后将每个workers中的闲置线程中断，当线程接收到中断的时候，会从`#getTask`的阻塞中跳出来，重新检查两个地方：

1. 队列是否为空
1. 当前状态是否是STOP（调用shutDownNow方法）

```java
private Runnable getTask() {
    boolean timedOut = false; // Did the last poll() time out?

    for (;;) {
        int c = ctl.get();
        int rs = runStateOf(c);

        // Check if queue empty only if necessary.
        if (rs >= SHUTDOWN && (rs >= STOP || workQueue.isEmpty())) {
            decrementWorkerCount();
            return null; // 如果是shutDown则退出
        }

        // ... 省略代码
    }
}
```


如果符合，则`#getTask`会返回null，此时，工作线程进入进入`#processWorkerExit`关闭当前工作线程，再进入`#addWorker`方法，会发现，此时也有两点：

1. STOP状态
1. SHUTDOWN且队列为空
```java
private boolean addWorker(Runnable firstTask, boolean core) {
    retry:
    for (;;) {
        int c = ctl.get();
        int rs = runStateOf(c);

        // Check if queue empty only if necessary.
        if (rs >= SHUTDOWN &&
            ! (rs == SHUTDOWN &&
               firstTask == null &&
               ! workQueue.isEmpty()))
            return false; // 此时便不会新增worker

    // ... 省略代码
    return workerStarted;
}
```

如果符合，则不会再新创建线程。
**核心**：**通过中断线程，将闲置线程从**`**#poll**`**中解放出来，并且关闭；如果是shutDown状态，则需要等到任务执行完才可以关闭；如果是stop状态，则不会等到任务执行完，就会关闭**

#### 线程池相关知识

看完`ThreadPoolExecutor`的代码后，我特地抽时间画了一张图，希望可以加深自己的理解：

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/5a6672af_java-threadpool-throw-ex-4.jpeg" align="middle" />

同理，`ScheduledThreadPoolExecutor`作为`ThreadPoolExecutor`的子类，基本上大差不差。与其最大的不同之处就在于队列：定时线程池自定义了`DelayedWorkQueue`队列，work线程从队列中获取任务时，队列会去判断时间，只有时间满足，才会将任务出列。同时在任务被执行完成后，定时线程池会将该任务重新入队，便于之后重新调用