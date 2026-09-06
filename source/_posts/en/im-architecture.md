---
title: An Overview of Instant Messaging System Architecture
date: 2021-01-15 19:41
tags:
  - 系统设计
  - 消息队列
  - 分布式系统
categories:
  - 架构思考
description: >-
  Systematically reviews IM architecture design, including communication flows
  for one-to-one chat, group chat, and push; message persistence and
  synchronization; Redis cache-failure guarantees; and choices and optimizations
  involving Netty, write fan-out, and cluster routing.
lang: en
translation_of: im-architecture
---

The IM system built by my team needs optimization, and it is also the topic of my graduation project. So I recently took time to summarize its current processes and architecture. I benefited greatly, especially from studying the communication flow and synchronization approach.

However, cache failure, performance optimization (clusters, caching, asynchrony, and batch processing), and code abstraction are still not handled well enough, and I need to improve them next.

### I. Communication flow

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/85a7042f_ims-flow.png" align="middle" />

### II. Basic functions

After users come online, their information is stored in Redis to facilitate later message sending and receiving. Stored information includes the user's channel, ack, token, seq, online-user count, and so on.

#### 1. One-to-one chat (C2C)

The one-to-one logic is relatively simple. After a sender sends a message to the server over a long connection, the server forwards the message (through RPC/RESTful) to route. After route persists the message and sequence number, it forwards the message to the receiver's channel through the Redis cache.

#### 2. Group chat (C2G)

We abstract group chat and one-to-one chat into essentially the same logic, treating a group as a receiver as well.

The receiver in group chat is `groupId`. In the second business-processing step, the receiver's `groupId` is used to query the database for all group members. The Server then forwards the message to every member, and messages are sent through their channels.

#### 3. Push (S2C)

Push cannot use write-fan-out optimization through `groupId`, so it can write a large number of messages and heavily update receivers' `ack_seq` and `msg_seq`. Push therefore needs additional optimization.

### III. Message synchronization

#### 1. Persistence approach

`msg_seq` stores a message's sequence number and increments by `receiverId`. `last_ack_seq` stores the acknowledged sequence. The server stores acks because, if it did not, users could not obtain unread messages after switching phones.

1. group: `msg_seq`
2. group_user: `last_ack_seq`
3. message: `msg_seq`
4. user: `last_ack_seq` `msg_seq`

One-to-one chat: persist the message; increment the user's `msg_seq` **by `userId`**; update persisted data (1%); update the user's `ack_seq` (1%).

Group chat: persist the message; increment the group-chat `msg_seq` **by `groupId`**; update persisted data (1%); update a user's group-chat `ack_seq` (1%). **[When a group has many users and they see messages at the same time, even a 1% probability of persisting instant ack confirmations may overwhelm the database.]**

#### 2. Synchronization flow

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/f7d77102_ims-offline.png" style="zoom: 67%;" />

#### 3. Cache failure

Because `msg_seq` and `ack_seq` are stored in Redis and synchronized to the DB only with a 1% probability, how can we ensure that users can synchronize unread information when Redis fails? This is a problem.

> **The following assumption is based on user1 being offline.**
>
> Suppose that in one C2C interaction, user1's `msg_seq` has just been persisted. At this point `user1_msg_seq` is 100 in the database and 100 in Redis. User1 subsequently receives messages normally as receiver, but the persistence mechanism is not triggered.
>
> Some time later, `user1_msg_seq=100` in the database (because the 1% chance was not triggered) while `user1_msg_seq` is 200 in Redis. This means user1 has received another 100 messages that have not yet synchronized to the DB, and Redis now goes down.

At that point user1's 100 messages are lost. The previous solution was to retrieve the old sequence from the database and add a step of 10,000. With 1% persistence, 10,000 can almost guarantee a value larger than the failed Redis sequence.

`ack_seq` does not have this problem because our ack comes from the client. In other words, the server's ack is **stateless**, so there is no need to consider a 10,000 step.

#### 4. Out-of-order messages

If the sender sends messages in the order 1, 2 but the receiver receives them in the order 2, 1, how should this be handled?

We need to include the message's `createTime` when sending it, then have the client readjust the order within an appropriate range based on `createTime`.

#### 5. Optimization options

1. **Messages may be synchronized several times in small batches; there is no need to synchronize all unread messages at once**, similar to paginated queries.
2. MQ can be used as a buffer. For push in particular, because immediacy is unnecessary, **MQ can smooth peaks and valleys**.
3. For messages sent over long connections, extra persistence can also be done by a separate thread or an **asynchronous persistence** message queue (message synchronization may then be delayed), though consistency between sending and storage cannot be guaranteed.
4. Persistence should not use a percentage: one percent corresponds to 10,000, which is costly. A fixed step can be considered.
5. Acks cannot be persisted every time (1%); they should also be persisted **by step** [refer to WeChat].

### IV. Trade-offs

#### 1. Server choice

Tomcat or Netty: native connections based on Netty are provisionally selected. For simplicity and ease of use, Yeauty is selected as WebSocket scaffolding to ease migration from Tomcat to Netty. But using Yeauty fixes the transport format and loses Netty's benefits for custom network transport.

#### 2. Communication protocols

* Long connection: WebSocket over TCP or custom parsing over TCP; ProtoBuf over TCP is provisionally selected.
* Short connection: RESTful is used currently, with a later hope of moving to RPC.

#### 3. Read and write fan-out

Read fan-out or **write fan-out**: write fan-out is currently used. For our business, when group sizes are controlled and concurrency is not high, write fan-out is easier to implement.

At the same time, treat the group ID as a receiver as well, preventing excessively large groups from increasing write-fan-out pressure. A message entity is stored only once, while `ack_seq` and `msg_seq` are updated randomly.

### V. Architecture issues

#### 1. Service deployment

Deploy Netty as a cluster.

**How does a multi-server setup route to the receiver's channel?** — A route service is needed in front for routing.

**How are services on each server registered and discovered?** — A registry is needed, perhaps Redis or ZooKeeper.

#### 2. Business abstraction

The basic chat pipeline and business modules such as creating groups and managing friends need to be abstracted, then provided externally as an SDK.

#### 3. Message reachability

When a sender successfully sends a message or a receiver successfully receives one, each sends an ack to the server to indicate successful receipt.

### VI. Monitoring issues

At present only the online-user count can be monitored, which is still insufficient.
