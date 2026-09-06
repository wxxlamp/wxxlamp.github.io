---
title: Handling Message Idempotency in Queue Consumers
tags:
  - 消息队列
  - 分布式系统
  - 数据库
categories:
  - 场景实践
date: 2023-05-07 10:36
description: >-
  How to solve idempotency problems caused by repeated message-queue
  consumption, covering distributed locks, unique indexes, special SQL, and
  exclusive locks, with an analysis of MySQL locking.
lang: en
translation_of: how-to-deal-msg-reconsume
---

Recently, while integrating with another business, I found a problem:

> When consuming messages from an upstream business, an unusual upstream situation caused multiple messages to be sent at the same time (status-change messages, with the status changing several times in one moment). Since the consumer had no idempotency protection, it consumed the messages repeatedly. In this case, that resulted in two rows being inserted.

How do we solve it? It is actually simple: lock the conflicting resource. There are several approaches.

## Approach 1: Distributed lock

1. Add a distributed lock to the current consumption logic by user.
2. If it has already been consumed, do not consume it again.
3. If it has not been consumed, consume it.

The pseudocode is:
```java
public void consume(Message msg) {
	String id = msg.getId();
	RedisLock.acquire(id, msg -> {
        Record record = db.query(msg);
        if(record != null) {
            return;
        }
        process(msg);
    });
}
```

## Approach 2: Database unique index

Most current Web services are deployed as clusters, so a lock must be distributed. Although databases may use sharding, for the same shard key a record from one consumption will always land in one physical database and one physical table.
We can therefore use a unique index on the single physical database and let the database provide the lock. If insertion fails, simply catch an exception such as `Duplicate entry`.

## Approach 3: Special SQL statements

These essentially also depend on a unique index.

### insert ignore

`insert ignore` ignores data already present in the database (determined by the primary key or unique index). If no data exists, it inserts a new row; if data exists, it skips the row.
```sql
 insert ignore into sc (name,class,score) values ('张三','三年二班',90)
```
Running the statement produces no error, but the primary key still auto-increments.

### replace into

`replace into` first attempts to insert data into the table. If the row already exists (determined by the primary key or unique index), it **first deletes the row and then inserts a new one**; otherwise it inserts a new row directly.

```sql
replace into sc (name,class,score) values ('张三','三年二班',90);
```

### insert on duplicate key update

- If `on duplicate key update` is specified at the end of an `insert into` statement and inserting the row would create a duplicate value in a UNIQUE index or PRIMARY KEY, the duplicate row is updated. If there is no duplicate, a new row is inserted as with an ordinary `insert into`.
- If a new row is inserted, the affected-row count is 1; if an existing row is updated, it is 2; if the value is unchanged before and after the update, it is 0.

```sql
insert into sc (name,class,score) values ('张三','三年二班',90) on duplicate key update score=100;
```

## Approach 4: Transaction + exclusive lock

InnoDB reads use MVCC, so an ordinary `select` does not block. We can use a database transaction to lock during the query. Other queries are then blocked, and we insert if nothing is found. The SQL is:

```sql
select * from c where name = '张三' for update;
```

Approach 4 resembles approach 1, except approach 1 locks at the service level while this approach uses a database lock. The following examples use the RR isolation level.

### The relationship between indexes and locks

#### Primary-key index

Start a transaction with an indexed `where` condition:

```sql
begin;
select * from article where id = 3 for update ;
```

The lock state is:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/d2b6d8dd_how-to-deal-msg-reconsume-2.png" align="middle" />

Both the table and row are locked: the table has an intention-exclusive lock, and the row has a standard exclusive lock (only the record, not the gap). Therefore, another transaction attempting an exclusive-lock SQL statement will fail:

```sql
select * from article where id = 3 for update ;
update article set name='ck' where id = 3;
```

> PS, the purpose of an intention lock:
> Without an intention lock, obtaining an exclusive table lock would require traversing every record to check whether any record had an exclusive lock, which would be slow.
> With an intention lock, an intention-exclusive table lock is added before an exclusive record lock. When obtaining an exclusive table lock, we can simply check whether the table has an intention-exclusive lock. If it does, records in the table already have exclusive locks, so there is no need to traverse them.
> Therefore, **the purpose of an intention lock is to quickly determine whether any record in a table is locked**.

#### No index

Start a transaction with the following condition:

```sql
begin;
select * from article where author_id = 1 for update ;
```

The lock state is:
<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/62261fbf_how-to-deal-msg-reconsume-1.png" align="middle" />
We can see that the table also has an intention-exclusive lock. However, every record receives a fully exclusive lock (locking both the row and the gap), effectively locking the entire table. This is dangerous because other transactions cannot perform locking operations on the table.

### Locking when there is no match

For a case without an index, the locking logic is the same as for a match. Here we look at how locking works when there is an index but no match.

```sql
begin;
select * from article where id = 3 for update ;
```

The lock state is:
<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/d7aa5d63_how-to-deal-msg-reconsume-3.png" align="middle" />
The row receives a fully exclusive lock covering the range from 3 to positive infinity. Nothing can be inserted or updated between 3 and positive infinity.

> primary key value(s) of the locked record if LOCK_TYPE='RECORD', otherwise NULL. This column contains the value(s) of the primary key column(s) in the locked row, formatted as a valid SQL string (ready to be copied to SQL commands). If there is no primary key then the InnoDB internal unique row ID number is used. If a gap lock is taken for key values or ranges above the largest value in the index, LOCK_DATA reports “supremum pseudo-record”. When the page containing the locked record is not in the buffer pool (in the case that it was paged out to disk while the lock was held), InnoDB does not fetch the page from disk, to avoid unnecessary disk operations. Instead, LOCK_DATA is set to NULL

## References

1. [How MySQL locks (in Chinese)](https://xiaolincoding.com/mysql/lock/how_to_lock.html#%E5%94%AF%E4%B8%80%E7%B4%A2%E5%BC%95%E7%AD%89%E5%80%BC%E6%9F%A5%E8%AF%A2)
2. [Detailed MySQL locking process (in Chinese)](https://blog.51cto.com/u_15905482/5919949)
3. [What lock does Select for update acquire? (in Chinese)](https://www.51cto.com/article/744551.html)
