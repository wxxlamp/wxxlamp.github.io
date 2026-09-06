---
title: Protocols and Scheduling Patterns for Microservice Interaction
tags:
  - 分布式系统
  - 系统设计
categories:
  - 场景实践
date: 2022-05-04 21:36
description: >-
  A systematic review of core conventions and scheduling schemes for
  interactions among microservices. It covers exception conventions, four-field
  response design, idempotency conventions, and scheduled retries, compares
  synchronous RPC with asynchronous MQ, and helps establish a complete
  understanding of microservice interaction.
lang: en
translation_of: microservice-interaction
---

The main applications of computers on the internet are storing, processing, and displaying business data. Storage corresponds to big data, processing corresponds to Web services, and display corresponds to client development for H5, PC, iPhone, Android, and other platforms.

Web services alone are the main carriers of complex business. As the internet has developed rapidly, Web services have also evolved quickly, from a single node to clusters, Microservices, ServerLess, and ServerMesh. No matter how they evolve, they all rely on a single responsibility: dividing services according to business responsibilities, with each service corresponding to one business node, thereby achieving decoupling.

For a node in a Microservice, one important technical role while it completes its business logic is to connect what comes before and after it. The core of this role is interaction with upstream and downstream services.

### 1. Protocols and conventions

During interaction, the interaction standards must first be determined, including the interaction protocol, status codes, return values, and other cases.

#### Exception conventions

In theory, a downstream service provider should not throw exceptions to an upstream consumer. This makes the consumer pay an extra cost to catch exceptions and requires additional conventions for various exception cases, increasing the cost of interaction and communication.

In RPC calls, however, the consumer must handle timeout exceptions. This is a problem that the service provider has difficulty preventing or controlling. Therefore, during an RPC call, the consumer only needs to catch timeout exceptions and retry. Other problems should all be agreed on and resolved through return values.

#### Return-value conventions

Generally, an interaction response has four fields: `success`, `code`, `msg`, and `data`.

1. `success`: indicates whether the interaction succeeded, generally with either `true` or `false`.
2. `code`: indicates the response code and generally takes effect when `success=false`. Common code categories include invalid parameters, abnormal state, concurrency exceptions, and system exceptions.
3. `msg`: explains the interaction and generally takes effect when `success=false`, providing details about the code.
4. `data`: contains the specific data from the interaction.

#### Idempotency conventions

The concept of idempotency comes from mathematics. With all other conditions unchanged, it means that no matter how many times a consumer sends a request, its impact on the downstream service and the resulting service response remain unchanged.

*For example, under HTTP's RESTful protocol, the GET method should be idempotent.*

For modification or creation operations, the provider's system data must not change because of repeated consumer requests, and the response should be as close as possible to the first response (whether it must be identical can be agreed by both parties). Generally, there are two situations:

1. The interaction causes the provider to begin creating a document. If the first interaction creates it successfully, the provider should do nothing and return directly when the same request arrives again.
2. The interaction advances the state of a document previously created by the provider. When the same request arrives again, the provider should check the local document's state. If its state has already advanced, it should do nothing and return directly.

#### Retry conventions

When an exception occurs or the downstream provider has a problem during an interaction, the interaction may fail to take effect. A scheduled task is then needed to retry it. Common retry cases include:

1. The downstream service throws a timeout exception.
2. The downstream service encounters concurrency and discards the request.
3. The downstream service is unavailable.

### 2. Scheduling schemes

Interaction scheduling is also important. In basic microservice operations, there are two common schemes: real-time synchronous scheduling and non-real-time asynchronous message scheduling.

#### Synchronous and asynchronous

The synchronous interaction discussed here differs somewhat from the synchronous/asynchronous and blocking/non-blocking concepts we normally use. In this article, synchronous interaction is defined from the provider's perspective: after receiving a request, the provider processes it immediately and then immediately returns a result to the caller. Common synchronous interactions include RPC; HTTP is also a synchronous interaction (excluding long connections).

Asynchronous interaction is an MQ-based, message-driven interaction model. A common path is: an upstream service sends a message to MQ, MQ forwards it downstream, and the downstream service processes it. After processing, the downstream service may send a message to MQ, which forwards it to other services consuming that message. Asynchronous MQ interaction fully decouples upstream and downstream. Its latency is higher than synchronous interaction, so it is generally used to drive the state machines of upstream and downstream services.

#### Real-time and scheduled

Real-time interaction is relative to scheduled interaction. Real-time interaction happens immediately, while scheduled interaction is triggered only at a given point or period of time. Scheduled interactions generally use a cron expression to specify when they run.

In everyday business scenarios, scheduled scheduling is used frequently—for example, scheduling retries for failed operations, updating files on a schedule, and refreshing caches regularly.

PS: I have not discussed Docker or Kubernetes, nor big data and storage (Hadoop, Flink, Spark, HBase), and I have not analyzed each part deeply enough. More updates will follow....
