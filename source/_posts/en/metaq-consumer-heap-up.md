---
title: Troubleshooting a MetaQ Consumer Backlog
tags:
  - 消息队列
  - 问题排查
categories:
  - 采坑记录
date: 2023-04-25 21:36
description: >-
  A consumer-backlog investigation triggered by migrating from Spring Cloud
  Stream to native MetaQ configuration. Source analysis shows that one
  ConsumerGroup can map to only one MQConsumerInner; using separate
  ConsumerGroup IDs resolves it.
lang: en
translation_of: metaq-consumer-heap-up
---



> Note: MetaQ is an internal Alibaba product whose open-source version is called RocketMQ.

## Symptoms

For special reasons, one application in the business I owned needed its messaging configuration changed from Spring Cloud Stream to native MetaQ. The configurations before and after the change were:

```properties
spring.cloud.stream.bindings.consumerA.group=CID_CONSUMER_A
spring.cloud.stream.bindings.consumerA.contentType=text/plain
spring.cloud.stream.bindings.consumerA.destination=CONSUMER_A_TOPIC
spring.cloud.stream.metaq.bindings.consumerA.consumer.tags=CONSUMER_A_TOPIC_TAG

spring.cloud.stream.bindings.consumerB.group=CID_CONSUMER_A
spring.cloud.stream.bindings.consumerB.contentType=text/plain
spring.cloud.stream.bindings.consumerB.destination=CONSUMER_B_TOPIC
spring.cloud.stream.metaq.bindings.consumerB.consumer.tags=CONSUMER_B_TOPIC_TAG

spring.cloud.stream.bindings.consumerC.group=CID_CONSUMER_A
spring.cloud.stream.bindings.consumerC.contentType=text/plain
spring.cloud.stream.bindings.consumerC.destination=CONSUMER_C_TOPIC
spring.cloud.stream.metaq.bindings.consumerC.consumer.tags=CONSUMER_C_TOPIC_TAG
```
```properties
spring.metaq.consumers[0].consumer-group=CID_CONSUMER_A
spring.metaq.consumers[0].topic=CONSUMER_A_TOPIC
spring.metaq.consumers[0].sub-expression=CONSUMER_A_TOPIC_TAG
spring.metaq.consumers[0].message-listener-ref=consumerAListener

spring.cloud.stream.bindings.consumerB.group=CID_CONSUMER_A
spring.cloud.stream.bindings.consumerB.contentType=text/plain
spring.cloud.stream.bindings.consumerB.destination=CONSUMER_B_TOPIC
spring.cloud.stream.metaq.bindings.consumerB.consumer.tags=CONSUMER_B_TOPIC_TAG

spring.cloud.stream.bindings.consumerC.group=CID_CONSUMER_A
spring.cloud.stream.bindings.consumerC.contentType=text/plain
spring.cloud.stream.bindings.consumerC.destination=CONSUMER_C_TOPIC
spring.cloud.stream.metaq.bindings.consumerC.consumer.tags=CONSUMER_C_TOPIC_TAG
```

When half the machines had been deployed and we began observing the canary rollout, messages started accumulating:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/a563e111_metaq-consumer-heap-up-1.png" align="middle" />

## Cause

### Inconsistent Message Subscriptions

Based on past experience, I suspected that machines in the consumer group had inconsistent subscription relationships. Some subscribed to A and others to B, so MetaQ could not determine whether to consume the messages and left them accumulating on the broker. The MetaQ console confirmed that inconsistent subscriptions had caused the backlog.

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/19657061_metaq-consumer-heap-up-2.png" align="middle" />

The subscription on the deployed machine was:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/e1890480_metaq-consumer-heap-up-3.png" align="middle" />

The undeployed machine had the following subscriptions, clearly more than the deployed machine:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/50585be8_metaq-consumer-heap-up-4.png" align="middle" />

### Spring Cloud Stream and Native MetaQ

This raised another question: why did the subscriptions for the same `ConsumerId` change after replacing Spring Cloud Stream with native MetaQ?

More simply, when MetaQ and Spring Cloud Stream used the same `ConsumerId`, why did MetaQ's subscriptions overwrite Spring Cloud Stream's subscriptions?

> Note: one `consumerId` can subscribe to multiple topics.

The only way to answer this was to inspect the startup source code of Spring Cloud Stream and MetaQ.

#### MetaQ

The MetaQ client's class diagram is shown below:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/ead0ccb5_metaq-consumer-heap-up-5.png" align="middle" />

- `MQConsumerInner` records how the current `consumerGroup` interacts with the server and maps topics to tags. Its default implementation is `DefaultMQPushConsumerImpl`, with a one-to-one relationship to `consumerGroup`.
- `MQClientInstance` centrally manages reusable objects such as network connections. A map maintains the relationship between `ConsumerGroupId` and `MQConsumerInner`. Put simply, one `ConsumerGroup` can correspond to only one `MQConsumerInner`, as shown below:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/bb273e43_metaq-consumer-heap-up-6.png" align="middle" />

#### Spring Cloud Stream

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/3c942beb_metaq-consumer-heap-up-7.png" align="middle" />

Spring Cloud Stream is a glue layer between Spring and middleware. When it starts, it also registers a `ConsumerGroup`, as shown below:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/c4d6e249_metaq-consumer-heap-up-8.png" align="middle" />

### Root Cause

At this point, the cause is clear. During startup, Spring Cloud Stream creates its own `MetaPushConsumer`, which is effectively a new `MQConsumerInner`. One `ConsumerGroup` therefore has two `MQConsumerInner` instances, violating MetaQ's required one-to-one mapping. By default, MetaQ replaces the old mapping with the new one. The native MetaQ consumer consequently replaces Spring Cloud Stream's consumer.

That is why, for `ConsumerA` on deployed machines, only the native MetaQ subscription remained.

## Solution

Change the consumer ID:

```properties
spring.metaq.consumers[0].consumer-group=CID_CONSUMER_A
spring.metaq.consumers[0].topic=CONSUMER_A_TOPIC
spring.metaq.consumers[0].sub-expression=CONSUMER_A_TOPIC_TAG
spring.metaq.consumers[0].message-listener-ref=consumerAListener

spring.cloud.stream.bindings.consumerB.group=CID_CONSUMER_B
spring.cloud.stream.bindings.consumerB.contentType=text/plain
spring.cloud.stream.bindings.consumerB.destination=CONSUMER_B_TOPIC
spring.cloud.stream.metaq.bindings.consumerB.consumer.tags=CONSUMER_B_TOPIC_TAG

spring.cloud.stream.bindings.consumerC.group=CID_CONSUMER_B
spring.cloud.stream.bindings.consumerC.contentType=text/plain
spring.cloud.stream.bindings.consumerC.destination=CONSUMER_C_TOPIC
spring.cloud.stream.metaq.bindings.consumerC.consumer.tags=CONSUMER_C_TOPIC_TAG
```

## Reflections and Summary

1. The cause was not complicated, but many people might stop at the first layer—an inconsistent subscription relationship caused the backlog. We still need the curiosity to investigate more deeply.
2. Avoid maintaining two sets of configuration in production wherever possible, because doing so adds cognitive overhead.
