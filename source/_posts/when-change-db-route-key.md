---
title: "当修改分库分表键时"
tags:
   - DB
categories:
   - 采坑记录
date: 2023-06-11 19:36
description: "本文记录了一次分库分表场景下的线上采坑经历。因代码bug需紧急订正用户数据，直接在物理库中修改了作为分库分表路由键的user_id字段，导致业务代码按修改后的值查询时无法命中正确的物理库表。文章分析了bigint类型与字符串类型路由行为的差异，揭示了修改路由键后数据"消失"的根本原因，并给出正确解法：应先删除原记录再重新插入，而不能直接update路由键字段。"
---



# 问题背景

因为代码bug，导致某项业务流程不符合预期，为了紧急修复工单用户，需要把数据表（分库分表）的user_id（bigint类型）从主账号改为子账号，但是在物理库订正之后，发现业务代码依据修改后的子账号查询不到了，如下所示：

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/13a141f5_when-change-db-route-key-1.png" align="middle"/>

但是如果我把key改为str的格式，就可以查到：

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/0159fa4f_when-change-db-route-key-2.png" align="middle"/>

这就很诡异了，对于bigint类型的字段，为啥带引号能查到，不带引号反而查不到呢？

# 问题原因
联想下订正前后，订正前不带引号也是可以查到的，所以又重新做了一个测试，即使用正常的数据（非订正）重新做一次查询。如下所示：

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/7b75cdd6_when-change-db-route-key-3.png" align="middle"/>

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/675f25c2_when-change-db-route-key-4.png" align="middle"/>

这说明什么呢？就是只有我订正的那条数据是有问题的。同时在使用其他账号查询的过程中，**发现如果使用bigint类型进行查询，则会非常快，如果使用str类型作为key值进行查询，则会变得很慢，会遍历所有的物理库寻找对应值。**

**然后看了下该数据库的分库分表键，果然，我查询和订正的user_id正是当前表的分库分表键**

问题原因就呼之欲出了：

因为订正的那条数据的字段刚好是分库分表键，所以在查询的时候，就会导致不能命中有数据的目标库表，导致查询不到数据。如下所示：

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/94725b23_when-change-db-route-key-5.png" align="middle"/>

按照原有的分库分表逻辑，user_id对应的记录应该落到0000库0000表中，当我们对0000库0000表的user_id进行修改后，这条数据还会存在于当前的物理库中。

但是修改后的user_id按照路由逻辑来讲应该落到0001库和0001表中的。所以当我们修改后，从代码中按照原有的分库分表逻辑到0001库0001表中查询，是肯定查询不到的

# 解决方案
订正分库分表键的时候，不能直接在逻辑库中update，而是要删除，然后重新插入（同时修改与date相关的字段）
# ONE MORE THING
之前在有次debug排查过程中，发现数据明明insert到数据库中了，但是在数据库中却查不到，后来发现是自己查的太急了，insert语句的所属的事务还没有提交，又因为数据库的隔离级别是RC，所以数据库是找不到的。
