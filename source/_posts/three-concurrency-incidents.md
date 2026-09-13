---
title: "三次并发问题排查：重复消费、锁竞争与查询超时"
date: 2026-09-13 23:11:20
tags:
  - "消息队列"
  - "并发编程"
  - "性能优化"
categories:
  - "采坑记录"
description: "记录三次后端并发问题排查：消息重复消费、主单锁竞争与串行查询超时，结合伪代码分析校验边界和吞吐瓶颈。"
---
![信封传送带汇入窄闸门，表现消息处理中的竞争与排队](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@43650cdcfd729e5bd3e43618ea27e7590179b7dc/images/d15431dc_cover.png)

笔者目前除了做 Agent 开发之外，日常的工作还涉及到淘宝天猫场景金融服务的后端开发。

最近三个月在 Codex 的协助下处理了很多日常的工单，其中涉及到一些并发场景导致的问题，在此和大家分享一下。

# 1. 消息重投递导致重复消费问题

大概在两个月前，我们通过核对发现一个客户的授信超时了。

问了下下游的核身服务，发现用户已经核身通过了，那为什么我们这边还没收到消息呢？

首先想到的就是上游消息没有发出来，但是通过日志，发现消息的确发到了我们这边。

那为什么会出问题呢？

原因就在于上游不仅发消息了，而且 MQ 还同时发了两条同样的消息过来。

> 这里使用的 MQ 中间件是 RocketMQ，按 at-least-once 语义处理，没办法保证不重复投递。

我们的机器在收到消息之后，会首先从数据库 load 数据，然后 check 状态，如果状态合法，则进入下一步的流程。伪代码如下：

```java
public void listener(Msg msg) {

    String bizId = msg.getId();
    CreditDO creditDO = mysqlDB.getData(bizId);
    if(!creditDO.canDoNext()) {
        return;
    }
    doNext(creditDO, msg);
}

@RedisLock(key = creditDo.id)
public void doNext(CreditDO creditDo, Msg msg) {
    // update
    update(creditDo, msg);
    // do next process
    // 如果幂等则直接返回
    signal(creditDo);
}
```

这个代码乍一看没有问题，但是如果两条消息同时来的话，就会出现两条数据都通过校验，然后串行执行 `doNext` 方法。对于第一个线程来说，它正常顺利执行没有问题。当第二个线程进入后，它又重新 update 了数据，但是要执行 signal 的时候，被下游服务的幂等逻辑拦住了，没办法继续执行。这样就会导致单据不一致的情况。

**正常的处理逻辑，应该严格 follow [“一锁二判三更新”](https://wxxlamp.cn/2023/05/07/how-to-deal-msg-reconsume/)的原则，即 query 和 check 逻辑也应该放到同一把有效的锁里面，避免两个线程都基于旧状态通过校验；跨服务一致性还需要事务与幂等机制配合。**

# 2. 锁粒度过大导致消息堆积问题

我们在特殊场景下，会有主子单的情况。

即把客户的一次申请，映射到该客户的符合条件的订单上进行处理。当所有订单处理完成之后，再更新主单的状态，将其置为完成。伪代码如下：

```java
// step1: 处理子单
public void payOrderItems(Order order) {

    for(OrderItem orderItem : order.getItems()) {
        payOrderItem(orderItem);
    }
}

// Step2：子单处理成功消息，通过消息投递
@RedisLock(key = orderItem.mainOrderNo)
public void onOrderItemPaySuccess(OrderItem orderItem) {

    // 校验主单状态
    queryDbCheckMainOrderStatus(orderItem);

    // 通过 Redis 扣减剩余子单计数
    redis.decrease(orderItem.getMainOrderNo());

    // 如果缓存记录子单数 为 0，则处理后续流程
    if (redis.get(orderItem.getMainOrderNo())  == 0) {
        doNextStep(orderItem.getMainOrderNo());
    }
}
```

在一个大客户的场景，客户的一次申请，同时触发了上万单的子单支付操作，然后在我们消费支付成功消息的时候，系统频繁抛出加锁阻塞异常，同时 MQ 的消费失败率显著提高。

仔细看了下当时的数据，同一笔主单，子单支付成功消息的 QPS 峰值在 700 左右。如果每条消息都直接更新数据库中的同一笔主单，就会集中竞争这一行的锁。所以代码在更新子单计数的时候，没有使用 MySQL，而是使用了 Redis，目的是避免主单的热点更新。

但是它加锁的维度是按照主单处理的，我们线上是 4C8G 的机器，Redis 锁内执行的一次数据库查询和 Redis 扣减大概花费 5ms，按同一把锁串行处理估算，理论上限约为 200 QPS，实际还要扣除加解锁等开销。这远小于 700 的峰值，就会导致大量的子单请求因为抢不到锁而消费失败，交给 MQ 做重投。重投的任务越多，短时间内堆积的消息就越多，那么系统接收到的消息也会越来越多（一共 2 万笔子单，因为失败重投，最后导致了将近 30 万次抢锁，流量放大了 15 倍），抢锁的失败率也会越来越高，这就是系统报警的原因。

![主单锁竞争与重投反馈：约700QPS消息争抢约200QPS临界区，2万子单触发近30万次抢锁](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@82edec8b77e149d2fbd07a05f99c4556b509554b/images/317838f8_main-order-lock.png)

所以，在这种主子单的场景，让每条子单消息都抢同一把主单锁，不是一个特别好的选择。

其实，如果这里的 decrease 封装的是 Redis DECR，单次扣减就已经是原子操作了，不必仅为扣减额外加一把悲观锁。但重复消息仍可能重复扣减，缓存计数只能用来触发检查，完成条件仍要在锁内查库确认，并校验主单状态、幂等推进。伪代码可以这么写：

```java
// Step2：子单处理成功消息，通过消息投递
public void onOrderItemPaySuccess(OrderItem orderItem) {

    // 校验主单状态
    queryDbCheckMainOrderStatus(orderItem);

    // 通过 Redis 扣减剩余子单计数
    redis.decrease(orderItem.getMainOrderNo());

    // 缓存记录子单数小于等于 20 时，才进入锁内查库
    if (redis.get(orderItem.getMainOrderNo())  <= 20) {

        redisLock.execute(key=orderItem.getMainOrderNo(), lockedOrder -> {
            // 1. 重新校验主单状态，并查库确认所有子单是否支付完成
            // 2. 如果全部支付完成，则幂等推进后续流程
        });
    }
}
```

# 3. 单线程查询导致任务超时问题

同样是一个大客户导致的问题。

这个客户有将近 4 万笔订单，需要同时处理，在调一个查询接口的时候，竟然因为历史原因使用了单线程，可以想象，即使每次 RPC 的时间只有 15ms，4 万笔串行调用也需要约 10 分钟，还没算其他处理开销。

刚好上游设置了这个任务超时时间是五分钟，在五分钟后来 check 的时候，发现部分单据还没有完成，补偿的时候就发生了报错。

这个问题太简单了，就不贴代码了。
