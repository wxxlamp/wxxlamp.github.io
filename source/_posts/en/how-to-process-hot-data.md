---
title: Handling Hot Reads and Writes
tags:
  - 性能优化
  - 数据库
  - 分布式系统
categories:
  - 场景实践
date: 2023-07-09 10:36
description: >-
  Using flash-sale scenarios as an example, this article discusses solutions for
  hot reads and hot writes: cache warming, large-key sharding, and multi-level
  caching for hot reads; inventory sharding, asynchronous Redis persistence, and
  application-level rate limiting for hot writes, while maintaining cache
  consistency.
lang: en
translation_of: how-to-process-hot-data
---

> We will use a flash-sale scenario throughout: skuId, skuContent, and skuStore.

# Hot Reads
Hot reads mean that skuContent must be displayed for a skuId. Since the database IO connection pool is fixed, the amount of data the database can handle is limited, so hot data needs to be synchronized to Redis.

## Cache Consistency

1. Deletion is preferable to updating, because updating is not an atomic operation.
2. If the cache is deleted first, then the database is updated and the cache is written back, inconsistency can occur during the write.
3. Therefore, use a delayed double-deletion strategy.

## Handling Hot Caches

The basic approach is to warm hot data in advance so requests do not hit the database directly. If traffic is so large that even Redis cannot handle it, consider these measures:

1. Shard large keys. For example, hash skuId into different keys using a consistent-hash algorithm and store them in Redis.
2. Use multi-level caches: keep one copy in the browser, CDN, local cache, and Redis.
3. Make requests in stages. For example, request the relevant hot data as soon as the user starts loading, so there is no need to request it again when the page is actually entered.

# Hot Writes

When a skuId becomes hot, database updates become a major problem too. Updating the database directly may produce a very high RT, because under the RC isolation level the row for that skuId is locked. The following approaches can be considered:

1. Distribute SKUs across different databases and decrement inventory there.
2. Decrement inventory in Redis, then send a message through Redis to the database for the decrement.
3. Write transaction details directly, then update inventory asynchronously from those details (the update must query the sum of the details).
4. Apply rate limiting at the application layer by skuId to prevent requests from reaching the database.
5. Create a hot-data database and move hot products into it.

Note: use optimistic locking to ensure consistency when deducting inventory.
