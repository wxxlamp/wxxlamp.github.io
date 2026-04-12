---
title: "制作和测试一把锁"
date: 2024-06-15 18:39
tags:
   - JAVA
   - 分布式
   - 系统设计
categories:
   - 架构思考
description: "本文详细介绍分布式锁的实现要点，涵盖可重试、可续期、加锁释放锁一致性等关键设计，包含完整的加锁业务逻辑和Redis连接异常处理策略，并提供Java实现代码示例。"
---

# 制作锁

编写分布式锁的注意点

1. 注意锁的可重试、可续期、以及加锁和释放锁的一致
2. 如果连接不上redis如何处理？如果线程抢占锁失败如何处理？

## 加锁业务逻辑
1. 包含业务要求的重试、以及redis连接不上、线程抢占锁失败的处理

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

## 内部锁加锁逻辑
1. 内部锁的粒度要控制，**以及如果两个锁释放失败如何处理**
2. 感觉也没必要加内部锁，因为如果并发度不高的话，每次都会获取到redis锁，再加上内部锁。反而降低了性能。如果单机并发很高，可以考虑加内部锁

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

## 核心加锁逻辑
1. 包含锁的可重入处理

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

## Redis连接逻辑
1. 包含redis连接不上的重试

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

# 测试锁
基于上面的分布式锁，当我想在单机上通过UT来保证锁的正确性，该如何写UT呢？

## 第一版
我写的第一版测试代码如下：

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

眼尖的同学可能一眼就看出来了程序的问题，主线程无法感知到测试结果。如果要保证主线程感知到测试结果，有两个需要注意的点，第一就是需要把测试线程的值传递给主线程。第二个点就是要保证主线程比测试线程执行的晚。常见的方式有 `CountDownLatch`、`BlockQueue`和共享内存等

## 第二版
所以我尝试写了第二版测试代码：

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

执行这个测试程序后，会有下面几个异常的case：

1. 31行的断言失败，firstThreadAns.get() == null![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/dbcd4d8e_8e094577.png)原因是因为14行，测试线程提前执行`latch.countDown()`，导致测试线程没有把测试结果传递给主线程，主线程就开始check结果
2. 主线程一直等待，导致程序不能结束![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/f9929e9f_9b8f3bf1.png)原因是因为第二个线程先执行，第一个线程没有获得到锁，抛出加锁失败异常，导致没有执行`latch.countDown()`方法，进行会导致主线程一直pending。解决方案很简单，就是保证第一个测试线程先于第二个测试线程执行。可以使用`Semaphore`、`CountDownLatch`和锁，但是这里要注意，不能用`Thread.join()`

## 第三版
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

完美

