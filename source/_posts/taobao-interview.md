---
title: "淘宝实习面试"
date: 2020-03-15 9:52
tags:
   - Java
   - Internships
categories:
   - 面试经验
description: "淘宝用户增长团队秋招提前批面试经验，涵盖Java基础、集合框架等相关问题。"
---

淘宝这边是西溪的用户增长团队，因为是秋招提前批，前两面过了之后需要录系统，我觉得不稳，然后就溜了

<!-- more -->


## 一面
### Java

#### 1. hashCode的作用

每个实例一个hash值，如果不覆盖则每个对象都不一样。常用来hashMap的桶定位

#### 2. 集合框架

Collection->list,st

Map

Stack和HashTable是线程安全的，ConcurrentHashMap和Cow也是

通过Collections.synchronizedList();

#### 3. AIO和BIO的区别

aio是异步的，bio是阻塞的

Jdk1.4之前是bio，Jdk1.7之后是aio

#### 4. 多线程的ABA问题

通过版本号机制来解决

#### 5. 线程池的执行原理

$$
execute() \rightarrow addWorker()\rightarrow Thread.start() \rightarrow runWorker() \rightarrow getTask() \rightarrow processWorkerExit()
$$

#### 6. Java的内存结构

堆，方法区，本地方法栈，虚拟机栈，程序计数器

#### 7. 什么时候Full GC和Young GC

eden满时是young Cc

old满时是full gc

### 框架

#### 8. Mybatis的$和#差异

> 刚开始听成占位符和#的差异了，这个地方交流误区，没听清所以浪费了时间

$：占位符，仅仅为一个纯碎的 string 替换，在动态 SQL 解析阶段将会进行变量替换

#：把传入的值作为字符串，防止SQL注入。解析为一个 JDBC 预编译语句（prepared statement）的参数标记符，一个 #{ } 被解析为一个参数占位符 。

#### 9. Spring bean的生命周期

new，注入，aware，前置，init，后置，注册回调函数，执行，执行回调函数，销毁

### MySQL

#### 10. 隔离级别

RU，RC，RR，S

#### 11. MySQL和Oracle的隔离级别

前者RR，后者RC

#### 12. 如何优化数据库的性能

优化字段

创建表的范式和反范式

索引，前缀索引，hash索引，组合索引

#### 13. 数据量太大怎么办

分库分表，每个表横向切分

#### 14. 分表主键唯一性

通过触发器在业务层面上约束

1. **UUID**：通过唯一识别码16个字节128位的长数字；**组成部分**：当前日期和时间序列+全局的唯一性网卡mac地；**优点**：代码实现简单、不占用宽带、数据迁移不受影响；**缺点**：无序、无法保证趋势递增（要求3）字符存储、传输、查询慢、不可读、可以逆向出mac地址不安全
2. **雪花算法**：表示符+时间戳+机器码+12位毫秒计数器；**优点**：自增，灵活度高；**缺点**：依赖机器的时钟，每个机器的时钟不可能完全同步
3. 通过mysql的auto_increment的间隔
4. 通过redis的步长来保证

[分布式主键创建方式](https://www.jianshu.com/p/9d7ebe37215e)

### 计算机网络

#### 15. session和cookie的区别

http是无状态的

Session是在服务端保存的一个数据结构，用来跟踪用户的状态，这个数据可以保存在集群、数据库、文件中；
Cookie是客户端保存用户信息的一种机制，用来记录用户的一些信息，也是实现Session的一种方式

### 数据结构

#### 16. 如何判断循环链表

快慢指针

#### 17. 怎么查看环的入口

slow pointer 到入口的顺时针距离为head到入口的距离

### 项目

#### 18. 说一下项目的流程

业务

#### 19. 项目的难点

并发肯定是因为TPS上不去，所以难点肯定是TPS这一块

包括redis缓存，还有消息队列（缓存雪崩（令牌限流访问，阿里数据库有款中间件），穿透（布隆过滤器过滤黑名单)）,缓存预热

令牌桶平滑流量，防止并发流量

最后一个是安全，防止脚本刷接口（限制请求次数redis的lru，验证请求头，生成动态秘钥），csrf，xss

还有一个是超买和少卖的问题

#### 20. 为什么做这个项目

#### 21. 两个域名如何实现登录态的共享

cookie不能跨域，这个是SSO

1. client访问a.com
2. a.com发现没有a_cookie，跳转到ssoServer
3. ssoServer发现没有sso_cookie，使client跳转登录界面
4. client登录后，ssoServer存储session，并使得client携带sso_cookie，此时把ticket发送给a.com
5. a.com拿到ticket后，请求ssoServer的ticket是否正确，如果正确，则设置client的a_cookie，登录成功
6. client访问b.com
7. b.com发现没有b_cookie，跳转到ssoServer
8. ssoServer发现有sso_cookie，即client已经登录，那么会把ticket传给b.com
9. b..com拿到ticket后，请求ssoServer的ticket是否正确，如果正确，则设置client的b_cookie，登录成功

[SSO-cnblog](https://www.cnblogs.com/ywlaker/p/6113927.html)

[SSO-aliyun](https://yq.aliyun.com/articles/636281)

#### 22. 如何保证Redis和MySQL的一致性

* 实时策略：删除Redis缓存，先更新MySQL，然后删除Redis的缓存（先写redis再写mysql，如果写入失败事务回滚会造成redis中存在脏数据）。第一个删除为了保证redis中没有该数据，第二个删除防止其他线程脏读
* 异步策略，更新redis，异步更新MySQL

[Redis缓存一致性](https://www.zhihu.com/question/319817091)

#### 23. 如何保证MQ的消息一致性和幂等性

**consumer如何确定把消息同步到数据库中**

首先通过MQ的事物保证redis和producer的一致性

producer-ack-broker-ack-consumer，通过ack来保证一直性

**MQ在重发消息的时候怎么保证幂等性**

可能生产者重发消息，也可能消费者重发消息。mq内部有一个记录消息消费成功的id，如果存在该id则不去消费

### 其他

#### 24. 平时有什么爱好

篮球唱歌

#### 25. 怎么刷基础理论

看面经和源码

#### 26. 有效的Java代码有多少行

5k行

#### 27. 实验室的矛盾怎么处理

## 二面

#### 1. 秒杀系统的关键点

#### 2. 令牌桶和漏桶

前者限制请求数目，后者限制请求速率

####  3. 如何反向增加库存

#### 4. Nginx的作用

缓存，负载均衡

#### 5. POST和GET

#### 6. HTTP和TCP长连接的不同

TCP维持长连接是需要保活机制的

HTTP的长连接是为了复用TCP的长连接，也就是说多个HTTP请求可以复用一个TCP连接

[HTTP的长短连接](https://www.jianshu.com/p/3fc3646fad80)

#### 7. 前沿技术

Docker，k8s，[云原生](https://yq.aliyun.com/articles/709088)，分布式，微服务，[Severless](https://www.zhihu.com/topic/20086226/hot)，[SeverMesh](https://www.cnblogs.com/xishuai/p/microservices-and-service-mesh.html)，区块链