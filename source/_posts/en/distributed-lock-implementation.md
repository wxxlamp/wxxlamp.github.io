---
title: Building and Testing a Distributed Lock
date: 2024-06-15 18:39
tags:
  - 分布式系统
  - 并发编程
  - 测试与质量
categories:
  - 架构思考
description: >-
  Distributed lock design with retries, renewal, consistent acquisition and
  release, Redis failure handling, and Java examples showing how to coordinate
  concurrent unit tests.
lang: en
translation_of: distributed-lock-implementation
---

# Building a Lock

Points to consider when implementing a distributed lock:

1. Support retries and renewal, and ensure consistency between lock acquisition and release.
2. What should happen if Redis cannot be reached? What should happen if a thread fails to acquire the lock?

## Business Logic Around Lock Acquisition

1. Include business-required retries and handling for Redis connection failures and unsuccessful lock acquisition.

```java
public static <T, R> R runWithLock(Function<T, R> function, T req, Class<? extends AssuranceSyncHandler<T,R>> clazz,
                                       int expiredSec, String... factors) {
    AssuranceSyncHandler<T, R> zedSynchronizedHandler = getSyncHandlerFromClazz(clazz);
    ZedBody zedBody = buildBody(req, expiredSec, factors);
    // 尝试加锁
    boolean lockSuc = tryLock(zedBody, zedSynchronizedHandler);
    // 如果没加锁成功，则按照配置策略进行重试
    if (!lockSuc && !retryLock(zedBody, zedSynchronizedHandler)) {
        LOGGER.info("thread can not get lock, retry times is {}", zedSynchronizedHandler.getRetryTimes());
        // 如果缓存不可用，则直接执行业务逻辑
        if (SmartZedThreadLocal.isSynchronizedLockInvalid()) {
            LOGGER.error("lock failed because of the system error, so func apply directly");
            SmartZedThreadLocal.clear(zedBody.getRowKey());
            return function.apply(req);
        }
        // 如果缓存可用，则执行自定义锁策略
        return zedSynchronizedHandler.strategyWhenSync(req);
    }

    R result;
    try {
        result = function.apply(req);
    } catch (Exception ex) {
        LOGGER.error("AssuranceLockUtils.runWithLock error when apply func", ex);
        throw ex;
    } finally {
        tryUnLock(zedBody);
    }
    return result;
}

@SuppressWarnings("unchecked")
private static <T, R> AssuranceSyncHandler<T, R> getSyncHandlerFromClazz(Class<? extends AssuranceSyncHandler<T,R>> clazz) {
    return Optional.ofNullable(clazz)
            .map(ApplicationContextUtil::getBean)
            // 此处加map是为了把子类转成父类
            .map(e -> (AssuranceSyncHandler<T, R>)e)
            .orElse((AssuranceSyncHandler<T, R>)defaultHandler);
}

private static boolean retryLock(ZedBody zedBody, AssuranceSyncHandler<?,?> handler) {
    int retryTimes = 0;
    boolean lockSuc = false;
    while(!lockSuc && handler.getRetryTimes() > retryTimes++) {
        lockSuc = tryLock(zedBody, handler);
    }
    return lockSuc;
}
```

## Internal Lock Acquisition

1. Control the granularity of the internal lock, and **consider what happens if releasing either of the two locks fails**.
2. An internal lock may not be necessary. With low contention, each call can acquire the Redis lock anyway, so adding a local lock reduces performance. Consider an internal lock when contention on a single machine is high.

```java
 private static boolean tryLock(ZedBody zedBody, AssuranceSyncHandler<?,?> zedSynchronizedHandler) {
    boolean ans = false;
    boolean innerTryLock = false;
    try {
        innerTryLock = LocalLockHolder.tryLock(zedBody.getRowKey(), zedSynchronizedHandler.getRetryInterval());
        if (innerTryLock) {
            ans = assuranceSyncService.lock(zedBody);
        }
    } catch (Throwable e) {
        LOGGER.error("AssuranceLockUtils.runWithLock error", e);
    } finally {
        // 如果外部锁没加成功，则释放内部锁
        if (!ans && innerTryLock) {
            LocalLockHolder.unlock(zedBody.getRowKey());
        }
    }
    return ans;
}

private static void tryUnLock(ZedBody zedBody) {
    try {
        LocalLockHolder.unlock(zedBody.getRowKey());
        assuranceSyncService.unLock(zedBody);
    } catch (Throwable e) {
        LOGGER.error("AssuranceLockUtils.runWithUnLock error", e);
    }
}

private static class LocalLockHolder {
    private static final Map<String, Lock> LOCK_MAP = new ConcurrentHashMap<>();

    public static boolean tryLock(String key, long timeout) throws InterruptedException {
        Lock lock = LOCK_MAP.computeIfAbsent(key, k -> new ReentrantLock());
        return lock.tryLock(timeout, TimeUnit.MILLISECONDS);
    }

    public static void unlock(String key) {
        Lock lock = LOCK_MAP.get(key);
        if (lock != null) {
            lock.unlock();
        }
        LOCK_MAP.remove(key);
    }
}
```

## Core Locking Logic

1. Include support for reentrant locking.

```java
public Boolean lock(ZedBody zedBody) {
    // 1. 竞争锁
    boolean suc = syncService.set(zedBody.getRowKey(), getValue(), zedBody.getTimeout(), () -> {
        // 如果redis没有连接上，则不加锁
        SmartZedThreadLocal.markSynchronizedLockInvalid(true);
        return null;
    });
    if (suc || isOwnLock(zedBody)) {
        // 增加引用次数
        int count = increaseCount(zedBody.getRowKey());
        LOGGER.info("lock suc key:{},threadId:{}, count {}", zedBody.getRowKey(), Thread.currentThread().getId(), count);
        return true;
    }
    return false;
}

@Override
public Boolean unLock(ZedBody zedBody) {
    int lockCount = threadLocal.get().getByKeyWithDefault(zedBody.getRowKey()).count.get();
    LOGGER.info("un lock start key:{},threadId:{},count:{}", zedBody.getRowKey(),
            Thread.currentThread().getId(), lockCount);
    // 1. 如果引用计数已经小于0，则失效缓存
    if (decreaseCount(zedBody.getRowKey()) <= 0) {
        return syncService.del(zedBody.getRowKey());
    }
    return true;
}

private int increaseCount(String key) {
    LockCounterHolder counterHolder = threadLocal.get();
    return counterHolder.increaseWithKey(key);
}

private int decreaseCount(String key) {
    LockCounterHolder counterHolder = threadLocal.get();
    return counterHolder.decreaseWithKey(key);
}

private boolean isOwnLock(ZedBody zedBody) {
    String s = syncService.get(zedBody.getRowKey());
    return StringUtils.equals(s, getValue());
}

private String getValue() {
    return LOCAL_HOSTNAME + ":" + Thread.currentThread().getId();
}

private static String getHostname() {
    try {
        return InetAddress.getLocalHost().getHostName();
    } catch (UnknownHostException e) {
        LOGGER.warn("Failed to get hostname", e);
        return "[unknown]";
    }
}

private static class LockCounterHolder {

    private final Map<String, LockCounter> counters = new HashMap<>();

    public LockCounter getByKeyWithDefault(String key) {
        return counters.computeIfAbsent(key, e -> new LockCounter());
    }

    public int increaseWithKey(String key) {
        LockCounter counter = getByKeyWithDefault(key);
        return counter.count.incrementAndGet();
    }

    public int decreaseWithKey(String key) {
        LockCounter counter = counters.get(key);
        // 防止非持有锁的线程释放锁
        if (counter == null) {
            throw new ZedSynchronizedException("key is not found when release. key=" + key);
        }
        int count = counter.count.decrementAndGet();

        if (count <= 0) {
            //如果count 小于0，删除key，避免内存泄漏
            counters.remove(key);
        }
        return count;
    }
}

private static class LockCounter {

    private final AtomicInteger count;

    public LockCounter() {
        this.count = new AtomicInteger(0);
    }
}
```

## Redis Connection Logic

1. Include retries when a Redis connection cannot be established.

```java
public boolean set(String key, String value, int expireTimeSec) {
    int connectTime = 0;
    String v = null;
    SetParams setParams = new SetParams().nx().ex(expireTimeSec);
    while (Objects.isNull(v)) {
        try (Jedis jedis = jedisPool.getResource()) {
            v = jedis.set(PREFIX + key, value, setParams);
            return StringUtils.equals(SUCCESS, v);
        } catch (Exception e) {
            LOGGER.error("rdb3 setNx error key:{} value:{}", key, value, e);
            if (connectTime++ >= RECONNECT_TIMES) {
                LOGGER.error("rdb3 retry {} times setNx error key:{} value:{}", RECONNECT_TIMES, key, value, e);
                throw e;
            }
        }
    }
    return StringUtils.equals(SUCCESS, v);
}
```

# Testing the Lock

Given the distributed lock above, how should I write unit tests on one machine to verify its correctness?

## First Version

My first test looked like this:

```java
@Test
public void testLockSync() throws InterruptedException {
    // 1. 第一个线程抢占到锁，睡眠
    new Thread(() -> {
        String res = AssuranceLockUtils.runWithLock((req) -> {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            return "test";
        }, null, 10, "test");
        Assert.assertEqual("test", res);
    }).start();
    // 2. 第二个线程尝试抢占锁，应该失败
    new Thread(() -> {
        try {
            AssuranceLockUtils.runWithLock((req) -> "test", null, 10, "test");
        } catch (Exception exception) {
            Assert.assertTrue(exception instanceOf ZedSynchronizedException);
        }
    }).start();
}
```

Sharp-eyed readers may immediately spot the problem: the main thread cannot observe the test results. Two things are necessary to fix this. First, pass the worker threads' results to the main thread. Second, ensure the main thread checks them after the worker threads have finished. Common approaches include `CountDownLatch`, `BlockingQueue`, and shared memory.

## Second Version

I therefore tried this second version:

```java
@Test
public void testLockSync() throws InterruptedException {
    CountDownLatch latch = new CountDownLatch(2);
    AtomicReference<String> firstThreadAns = new AtomicReference<>();
    AtomicReference<Exception> secondThreadAns = new AtomicReference<>();
    // 1. 第一个线程抢占到锁，睡眠
    new Thread(() -> {
        firstThreadAns.set(AssuranceLockUtils.runWithLock((req) -> {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                latch.countDown();
            }
            return "test";
        }, null, 10, "test"));
    }).start();
    // 2. 第二个线程尝试抢占锁，应该失败
    new Thread(() -> {
        try {
            AssuranceLockUtils.runWithLock((req) -> "test", null, 10, "test");
        } catch (Exception exception) {
            secondThreadAns.set(exception);
        } finally {
            latch.countDown();
        }
    }).start();
    // 3. 主线程check结果
    latch.await();
    Assert.assertEquals("test", firstThreadAns.get());
    Assert.assertTrue(secondThreadAns.get() instanceof ZedSynchronizedException);
}
```

Running this test exposes several failure cases:

1. The assertion on line 31 fails because firstThreadAns.get() == null. ![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/dbcd4d8e_8e094577.png) The worker calls `latch.countDown()` prematurely on line 14. The main thread starts checking before the worker has passed its result back.
2. The main thread waits forever, preventing the program from finishing. ![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/f9929e9f_9b8f3bf1.png) The second thread runs first, so the first thread fails to acquire the lock and throws an exception without calling `latch.countDown()`. The main thread remains pending. The solution is straightforward: ensure the first test thread reaches the required point before the second. A `Semaphore`, `CountDownLatch`, or lock can do this, but note that `Thread.join()` is unsuitable here.

## Third Version

```java
@Test
public void testLockSync() throws InterruptedException {
    CountDownLatch latch = new CountDownLatch(2);
    Semaphore semaphore = new Semaphore(0);
    AtomicReference<String> firstThreadAns = new AtomicReference<>();
    AtomicReference<Exception> secondThreadAns = new AtomicReference<>();
    // 1. 第一个线程抢占到锁，睡眠
    new Thread(() -> {
        firstThreadAns.set(AssuranceLockUtils.runWithLock((req) -> {
            req.release();
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            return "test";
        }, semaphore, 10, "test"));
        latch.countDown();
    }).start();
    // 2. 第二个线程尝试抢占锁，应该失败
    new Thread(() -> {
        try {
            semaphore.acquire();
            AssuranceLockUtils.runWithLock((req) -> "test", null, 10, "test");
        } catch (Exception exception) {
            secondThreadAns.set(exception);
        } finally {
            latch.countDown();
        }
    }).start();
    // 3. 主线程check结果
    latch.await();
    Assert.assertEquals("test", firstThreadAns.get());
    Assert.assertTrue(secondThreadAns.get() instanceof ZedSynchronizedException);
}
```

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/6cc2037a_ee446bac.png)

Perfect.

