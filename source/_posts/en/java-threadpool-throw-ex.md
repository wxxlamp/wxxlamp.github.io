---
title: Handling Exceptions in Java Thread Pool Tasks
tags:
  - Java
  - 并发编程
  - 问题排查
categories:
  - 采坑记录
date: 2022-08-09 23:36
description: >-
  Analyzes different behavior when thread-pool tasks throw exceptions under
  execute, submit, and schedule: execute throws directly and rebuilds the
  thread; submit requires get to observe the exception; schedule silently stops
  the periodic task. Explains the causes and solutions through source code.
lang: en
translation_of: java-threadpool-throw-ex
---

Recently I needed to use a thread pool for multithreading in an application. Sometimes logs and monitoring showed that an asynchronous task had suddenly stopped, leaving me bewildered and unable to investigate. A senior colleague eventually inspected the business code and found that a task in a new thread had thrown a runtime exception, causing the user thread I started to “fall over.” Why do threads in a thread pool not expose the exception? What state does a thread that throws an exception enter? This post analyzes that.

### Reproducing the cases
#### `#submit`

1. The task executed by the thread throws an exception, but it is not handled.
1. The user thread with the business exception does not “die”; it becomes `WATTING`.
1. The program continues to run.

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/dd569787_java-threadpool-throw-ex-1.png" align="middle" />

#### `#execute`

1. The task executed by the thread throws an exception, and it is successfully captured.
1. The user thread with the business exception ends directly and becomes `TERMINATED`.
1. The system does not end and continues running.

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/72c0a509_java-threadpool-throw-ex-2.png" align="middle" />

#### `#schedule`

1. The task executed by the thread throws an exception, but it is not handled.
1. The thread-pool thread is `WATTING`.
1. The program continues running, but the periodic task that threw the exception no longer runs.

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/d41f4b8a_java-threadpool-throw-ex-3.png" align="middle" />

### Cause analysis
#### #execute
For execute, this is easy to understand. The source code shows that when a thread-pool thread runs `runWorker`, if a task throws an exception, the thread throws it directly:
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
After an exception, to prevent the exceptional task from contaminating its thread, the worker that executed it is destroyed and a new non-core worker with no initial task is created. Therefore, even if every task in the pool fails, as long as the core-pool size is nonzero, the program remains blocked in `workQueue#poll` and the JVM does not exit.
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
`submit` is somewhat special because its task has a return value. When it is submitted, the pool wraps it in a `FutureTask`:
```java
public Future<?> submit(Runnable task) {
    if (task == null) throw new NullPointerException();
    RunnableFuture<Void> ftask = newTaskFor(task, null); // 封装该应用
    execute(ftask);
    return ftask;
}
```
Thus, when the pool runs `runWorker`, it actually enters the following method:
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
The explanation now becomes clear: `FutureTask` wraps the exception as the `outcome` Object. When `FuntureTask#get` calls `report`, it wraps and rethrows the exception as `ExecutionException`:
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
The pool thread is `WAITING` because after this task ends, `Worker` is blocked while calling `workQueue#poll`.

#### #schedule
`#schedule` executes in a scheduled thread pool. In theory, a task should still run periodically after throwing an exception, so why does it stop? Look at `ScheduledFutureTask`, a subclass of `FutureTask`: normally, after a scheduled task runs, its thread puts it back into the execution queue.
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
But in `#runAndReset`, an exception makes `#runAndReset` return false. The periodic task is then not requeued, so a scheduled task that throws an exception is not run again.
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
### Solutions

1. Catch and handle exceptions inside tasks so they do not interfere with thread-pool execution.
1. With `#execute`, use `ThreadFactory` to set logic for uncaught exceptions.
1. With `#submit` or `#schedule`, which invoke through `Callable`, call `#get` to explicitly handle task exceptions.

### Some thoughts
This problem is simple once thread pools are understood, but it exposed how insufficient my fundamentals were. I used to memorize interview material and could readily recite thread-pool `ctl` and every configuration; after some time, though, I was bewildered when actually using it and encountering a problem. As the saying goes: “What you have only read belongs to others; only what you have experienced is your own.”

#### How threads are shut down
When a thread pool shuts down, it closes some threads. How? On `#shutdown`, the pool traverses all workers and interrupts each idle thread. When an interrupted thread escapes the blocking `#getTask`, it checks two things again:

1. Whether the queue is empty.
1. Whether the current state is STOP (when `shutDownNow` is called).

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

If these conditions apply, `#getTask` returns null. The worker enters `#processWorkerExit` and closes itself. Entering `#addWorker` then reveals two further conditions:

1. STOP state.
1. SHUTDOWN with an empty queue.
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

If they apply, no new thread is created.
**Core idea**: **Interrupt idle threads to release them from** `**#poll**` **and close them. In SHUTDOWN state, they can close only after tasks finish; in STOP state, they close without waiting for tasks to finish.**

#### Thread-pool knowledge

After reading `ThreadPoolExecutor` code, I took time to draw a diagram to deepen my understanding:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/5a6672af_java-threadpool-throw-ex-4.jpeg" align="middle" />

Likewise, as a subclass of `ThreadPoolExecutor`, `ScheduledThreadPoolExecutor` is broadly similar. Its biggest difference is the queue: the scheduled pool customizes `DelayedWorkQueue`. When a worker gets a task, the queue checks time and dequeues it only when the time is met. After a task runs, the scheduled pool requeues it for later invocation.
