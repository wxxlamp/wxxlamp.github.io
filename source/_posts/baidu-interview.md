---
title: "百度三轮游"
tags:
   - JAVA
   - 校园招聘
categories:
   - 面试经验
date: 2020-10-15 10:36
description: "记录百度秋招三轮面试经历，涵盖Java基础、IO模型、线程池、数据库索引、分布式锁等核心知识点，附有LRU和对称二叉树代码实现。"
---

记得那是周五，一天连着四轮面试（上午两场+下午两场），上午是百度一面和shopee，下午两轮全是百度的

<!-- more -->

### 一面

1. String，StringBuffer， StringBuilder

   * String是由final修饰的类，同时它是由byte(9+)或者char(8-)数组组成的，这些数组也是final的
   * StringBuffer是线程安全的，StringBuilder是线程不安全的。StringBuffer是通过synchronized的方法级别来实现的
   * 对于StringBuffer和StringBuilder来说，他们有一个共同的父类，即AbstractStringBuilder，他们的属性和类都没有final修饰，所以导致了他们是可变的。相对来说，StringBuffer有自己的cache，保证了查询的性能，这个cache在builder中是没有的。

2. 接口和抽象类

   * 在JDK5之前，接口和抽象类在语法层面上有着显著的区别：接口不能有自己的方法体，同时接口只能是public的；抽象类可以有自己实现的方法，同时抽象类也可以有空方法
   * 随着JDK的升级，在Java8时，接口可以有default方法，到了Java9之后，接口也可以有自己的私有方法。接口除了属性默认是public final的之外，几乎和抽象类在语法层面，没有任何区别
   * 所以对于这两者的区别，我们要站在更高的的角度，从设计的层面去看它们之间的区别。在我看来接口的设计是自上而下的，而抽象类的设计是自下而上的。设计模式中的模板方法模式，就是用抽象类的一个较好的体现。

3. 锁

   * Java中的锁其实分为两大类，一个是悲观锁，一个是乐观锁。悲观锁指的是synchronized家族的，使用的时候包括`Object#notify()`、`Object#notifyAll()`和`Object#wait()`。乐观锁指的是由CAS包延伸出来的一系列锁，包括J.U.C中的`ReentrantLock`、`ReentrantReadWriteLock`，与之配合使用的是`Condition`
   * 对于Synchronized来说，它的锁粒度是对象级别的，默认是Class对象，也可以是我们指定的实例对象。当修饰方法的时候会在字节码的flags中表明为ACC_SYNCHRONIZED标识，该标识指明了该方法是一个同步方法，JVM 通过该 ACC_SYNCHRONIZED 访问标志来辨别一个方法是否声明为同步方法，如果有设置，则需要先获得监视器锁。当修饰代码块时，会在字节码中通过 `monitorenter` 和 `monitorexit` 执行来进行加锁。当线程执行到 `monitorenter` 的时候要先获得所锁，才能执行后面的方法。Synchronized随着JDK的演变做出了一系列优化，如轻量级锁，锁粗化，锁消除，自旋锁等等。
   * 对于`ReentrantLock`来说，是一种可重入锁。它对应两个内部类分别表示公平锁和非公平锁，都继承自Sync，而Sync继承自AQS。于公平锁的`tryAcquire()`来说，它比非公平锁多了一个`!hasQueuedPredecessors()`的判断，即检查如果**当前线程位于队列的最前面或队列为空**，才会让它获得锁
   * 相对于Synchronized，ReentrantLock需要手动获取释放，支持公平锁，选择性通知等等功能。

4. 大概说下集合，hashMap的并发问题，HashMap中key为NULL时存的位置

   * Java中的集合分为两部分，一个是java.util包下的集合，包括list,vector,map,set等，还有一个就是J.U.C包下的并发集合
   * 对于list来说，分为数组存储和链表存储，分别是ArrayList和LinkedList（数组存储中还有vector，不过其效率较低一般不用）。对于Map来说，分为HashMap，WeakHashMap、TreeMap和LinkedHashMap。对于HashMap来说，它通过拉链法来解决hash冲突的问题；对于TreeMap来说，他通过红黑树来对key进行排序；对于LinkedHashMap来说，它通过链表记录了每个key插入的顺序，可以通过它实现LRU算法；对于WeakHashMap来说，它类似于ThreadLocal中的Entry，都继承了WeakReference，当key不被引用的时候，可以下次GC的时候删除；对于Set来说，它的几个派生类都是由对应Map实现的
   * HashMap在1.7版本时，当Entry数组多线程扩容时，因为使用的是头插法，会导致出现一个循环的单链表，导致get死循环的问题（1.8时已经修复）。除此之外，并发put元素时有可能导致覆盖问题。
   * HashMap中key为null，hash的结果是0，它会被保存在entry[0]上

5. NIO和BIO

   * Java目前为止支持3种IO，分别是BIO，NIO和AIO。BIO对应OS的阻塞式IO，NIO对应着OS中的多路复用模型，AIO则是异步IO模型。
   * 阻塞式IO模型 BIO： 当用户线程发出IO请求之后，内核会去查看数据是否就绪，如果没有就绪就会等待数据就绪，而用户线程就会处于阻塞状态，用户线程交出CPU。当数据就绪之后，内核会将数据拷贝到用户线程，并返回结果给用户线程，用户线程才解除block状态，如`socket.accept()`

   - IO复用模型 NIO(select,poll,epoll)：Java NIO之前用的select，现在用的epoll。用户发出IO请求之后，有一个select线程去管理这些请求*(socket)*，它会不断阻塞轮询内核关于某事件的数据是否能准备好，没有事件准备好则会一直阻塞。适合连接数较多的情况；select基于long数组，将内核和用户态拷贝消耗大，有1024的限制；poll基于链表，没有大小限制；epoll基于map，通过事件通知方式，每当fd就绪，系统注册的回调函数就会被调用，将就绪fd放到ready队列里面，时间复杂度O(1)
     需要注意的是：多路复用IO模型是通过轮询的方式来检测是否有事件到达，并且对到达的事件逐一进行响应。因此对于多路复用IO模型来说，一旦事件响应体很大，那么就会导致后续的事件迟迟得不到处理，并且会影响新的事件轮询

6. 线程状态及转换

   * 线程共有六种基本状态，分别是`NEW`，`RUNNABLE`，`BLOCKED`，`WAITING`，`TIMED_WAITING`，`TERMINATED`
   * `NEW`：线程被new出来，但是没有调用start方法

   - `RUNNABLE`：分为运行态和就绪态。就绪态即在等待一些资源如CPU

   - `BLOCKED`：等待monitor的锁，一般是要进入`synchronized`块或者方法中的线程。这对应着`synchronized`中对象的`MonitorObject`的`_EntryList`队列

   - `WAITING`：当线程调用了`Object.wait()`,`Thread.join()`或者`LockSupport.park()`方法时，进入等待状态，直到使用`notify()`/`notifyAll()`,`LockSupport.unpark()`或者调用方法的线程结束

   - `TIMED_WAITING`：是一种特殊的等待状态，当线程调用了`Thread.sleep(long)`,`Object.wait(long)`, `Thread.join(long)`, `LockSupport.parkNanos(long)`或者`LockSupport.parkUntil(long)`方法时，进入超时等待状态

   - `TERMINATED`：线程已经完成执行，进入结束状态

7. 线程池

   * 线程池是一种池化技术，降低资源消耗，提高响应速度，提高现成的可管理性
   * 线程池有七个参数，分别是`corePoolSize`,`maxmumPoolSize`,`keepAliveTime`,`unit`,`workQueue`,`threadFactory`,`handle`，当任务来临时，线程池的线程数会逐渐增大到core，然后把多余的放到队列中，如果超过队列长度，则增加线程池数目至max，如果还继续增加，则通过handle进行拒绝。当线程空闲time时间后，会销毁到core的数目。
   * J.U.C提供四种常见的线程池，分别是fixed（执行固定线程数目），single（执行单个任务），cache（执行多个短期任务）和scheduled（执行周期性任务）。前两个等待队列无限长，后两个最大线程数无限大

8. 缓存一致性

   只要有缓存，就存在缓存和DB的一致性问题

   * 先更新数据库，再更新缓存的话：如果A更新数据库，接着B更新数据库，接着B更新缓存，接着A更新缓存，造成了数据库和缓存不一致的情况；同样，先更新缓存，后更新数据库也有一样的问题
   * 先删除缓存，再更新数据库：如果A删除了缓存，接着B去查数据库，B把脏值填入缓存中，A再更新数据库，此时缓存已经有值了，导致缓存和数据库不一致
   * 采用延时双删的方案，即先删除缓存，再更新数据库，然后延时再删除缓存。当缓存删除失败的时候，可以将失败的key发送至消息队列，重新消费

9. 有序数组的合并

   ```java
   public class Main {
       public int[] merge(int[] arrA, int[] arrLeft) {
           int aLen = arrOne.length, bLen = arrB.length;
           int[] ans = new int[aLen + bLen];
           int a = 0, b = 0;
           for(int i = 0; i < aLen + bLen; i ++) {
               if(a < aLen && b < bLen) {
                   ans[i] = arrA[a] > arrB[b] ? arrB[b ++] ? arrA[a ++];
           	} else if (a < aLen) {
                   ans[i] = arrA[a ++];
               } else if (b < bLen) {
                   ans[i] = arrB[b ++];
               }
           }
           return ans;
       }
   }
   ```

### 二面

1. 数据库索引

   * 对于MySQL来说，其索引是B+树的结构，二叉搜索树保证了索引是有序的，平衡二叉树保证了索引不会退化到链表的极端情况，B树降低了平衡二叉树的严格性，提高了构建效率，B+树将值放到叶子节点中，是的树变矮，提高IO效率
   * 除此B+树之外，还有Hash索引，全文索引，R-Tree索引。可以通过B+Tree索引创建业务性质的自适应Hash索引（这个Innodb也有一定的优化，其中腾讯在11月份还贡献了点优化的代码，详情可以查看腾讯技术工程公众号#一个即将写入MySQL源码的官方bug解决之路）
   * 索引还有一些概念如：聚簇索引，组合索引，主键索引，索引下推，唯一索引，最左原则，覆盖索引 ，前缀索引
   * 一些索引失效的场景包括：like违背最左原则，类型不匹配，使用！等

2. AQS

   * QS通过内置的FIFO双端双向链表来完成获取资源线程的排队工作，双端双向链表。该队列由一个一个的`Node`结点组成，每个`Node`结点维护一个`prev`引用和`next`引用，分别指向自己的前驱和后继结点。AQS维护两个指针，分别指向队列头部`head`和尾部`tail`。该队列中的`Node`有五种状态，分别是`CANCELLED`,`SIGNAL`, `CONDITION`,`PROPAGATE`和初始状态
   * 从使用上来说，AQS的功能可以分为两种：独占（如`ReentrantLock`）和共享（如`Semaphore`/`CountDownLatch `,`CyclicBarrier`/`ReadWriteLock`)。`ReentrantReadWriteLock`可以看成是组合式，它对读共享，写独占
   * 除了`ReentrantLock`外，还有三种常用的AQS组件，分别是`Semaphore`,`CountDownLatch`和`CyclicBarrier`

3. 字段太长为什么不去建立索引

   * 字段过长的话会使得索引的存储变得很大，同时查找起来也会降低效率
   * 所以我们不如使用前缀索引来尽可能降低索引的长度

4. 写一个LRU，并发的LRU该怎么写

   ```java
   class LRUCache {
   
           // 定义一个双向链表
       static class Node {
           Integer key;
           Integer value;
   
           public Node(Integer key, Integer value) {
               this.key = key;
               this.value = value;
           }
   
           Node pre;
           Node next;
       }
   
       // 用来快速定位节点和记录节点数量
       private HashMap<Integer, Node> map;
       // 虚拟头节点
       private Node dummyFirst;
       // 虚拟尾节点
       private Node dummyLast;
       // LRU的容量
       private int capacity;
   
       /**
        * 初始化方法
        * @param capacity 指定缓存的容量
        */
       public LRUCache(int capacity) {
           map = new HashMap<>(capacity);
           dummyFirst = new Node(-1, -1);
           dummyLast = new Node(-1, -1);
           // 建立虚拟头和虚拟尾节点的关系
           dummyFirst.next = dummyLast;
           dummyLast.pre = dummyFirst;
           this.capacity = capacity;
       }
   
       /**
        * 从缓存中获取数据
        * @param key 缓存的键
        * @return 缓存的值
        */
       public int get(int key) {
           // 如果map中没有这个key,证明没有命中缓存,直接返回-1即可
           if (!map.containsKey(key)) {
               return -1;
           }
           Node target = map.get(key);
           // 将命中缓存的节点移到链表的最末尾（虚拟尾节点前面）
           moveToTail(target, false);
           return target.value;
       }
   
       /**
        * 向缓存中写入数据
        * @param key 写入的键
        * @param value 写入的值
        */
       public void put(int key, int value) {
           // 如果这个map存在的话,只需要把这个节点移到链表的最末尾（虚拟尾节点前面）,并修改链表的值即可
           if (map.containsKey(key)) {
               moveToTail(map.get(key), false);
               map.get(key).value = value;
               return;
           }
           // 如果map不存在的话,需要在map和链表的最末尾（虚拟尾节点前面）新增这个节点,并且检查现在缓存超没超容量,如果超了的话需要删除链表的最前面的节点(虚拟头节点的后面)
           Node node = new Node(key, value);
           map.put(key, node);
           moveToTail(node, true);
           while (map.size() > capacity) {
               map.remove(dummyFirst.next.key);
               dummyFirst.next = dummyFirst.next.next;
               dummyFirst.next.pre = dummyFirst;
           }
       }
   
       /**
        * 将节点移动至链表的末尾，假末尾节点前面
        */
       private void moveToTail(Node node, boolean insert) {
           // 如果不是新增,而是修改,我们要维护原节点的pre和next节点的next和pre引用
           if (!insert) {
               node.pre.next = node.next;
               node.next.pre = node.pre;
           }
           // 将节点移动到链表的最末尾（虚拟尾节点前面）
           node.next = dummyLast;
           node.pre = dummyLast.pre;
           dummyLast.pre = node;
           node.pre.next = node;
       }
   }
   ```


### 三面

1. 分布式锁

   * 对于单机的锁来说，它只是一个所有线程/进程都能看到的一个**标记**而已。对于Java来说，synchronized是在对象头设置标记，Lock 接口的实现类基本上都只是某一个 volitile 修饰的 int 型变量其保证每个线程都能拥有对该 int 的可见性和原子修改；对于linux内核中来说，它也是利用互斥量或信号量等内存数据做标记。
   * 对于分布式情况来说，我们只要能找到一个公共标记被所有机器可以访问，就可以通过这个标记来完成分布式锁的性质。我们可以把这个标记放到公共内存中，如Redis，Memcache；也可以放在磁盘上，如数据库中；
   * 有了标记之后，我们要考虑这个分布式锁的性质，如是否可重入，是否公平，是否阻塞；考虑这个分布式锁的高可用和高性能；考虑这个分布式锁的实现方式，如乐观锁，悲观锁等等
   *  可以基于数据库的主键和版本号，Redis的SETNX()、EXPIRE()方法做分布式锁，也可以用Zookeeper来构建分布式锁

2. 集群的发现

   * 很多的中间件设计都会使用Zookeeper作为集群中组成员的发现机制，客户端会在Zookeeper上建立一个临时目录，Zookeeper会和客户端建立一条长连接，并且定时发送心跳，一旦发现客户端失活，Zookeeper就会删除当前客户端建立的临时节点，同时将消息发送给监听者。Zookeeper的这种特性被很多中间件应用作为集群发现机制。比如kafka使用Zookeeper维护broker和消费组的状态，Hbase使用Zookeeper选举集群的master，dubbo使用Zookeeper维护各个服务的实例存活状态（这个是从网上舶来的，因为我当时没理解面试官的意思，所以这个问题其实跳过了）

3. broker到consumer的消息不丢失

   * MQ的消息流程分为producer->broker->consumer，要保证消息不丢失，需要保证这两个传递过程的可靠性。面临的不稳定因素有网络异常，节点宕机等等。

   * RocketMQ采用了ack机制，如果consumer消费不到消息，broker会重复投递这个消息（投递次数可以自定义），直到消费成功，这里要保证消费接口的幂等性；同时，Consumer自身维护一个持久化的offset，标记这已经成功发回broker的下标 ，通过这个下标，即使Consumer宕机，也可以在重启之后到MessageQueue中拉去消息

4. aop的两种实现和原因

   * Spring AOP使用jdk动态代理和cglib。如果被继承者有接口的时候，使用JDK的动态代理，否则，则使用CGLIB
   * JDK的动态代理需要实现一个公共的接口（通过接口找到代理的方法），动态代理生成的反射类。Proxy是具体的代理，我们在实现了InvocationHandler之后的invoke方法会进入Proxy(*继承了Proxy，实现了接口*)的方法中
   * CGLib采用的是用创建一个继承实现类的子类，用asm库动态修改子类的代码来实现的，所以可以用传入的类引用执行代理类

5. 对称二叉树

   ```java
   import java.util.Scanner;
   public class Main {
       public static void main(String[] args) {
           //Scanner in = new Scanner(System.in);
           //int a = in.nextInt();
           //System.out.println(a);
           System.out.println("Hello World!");
       }
       private boolean judge(TreeNode root) {
           return dfs(root.left, root.right);
       }
       private boolean dfs(TreeNode left, TreeNode right) {
           if(left == null && right == null) return true;
           if(left == null || right == null) return false;
           return left.val == right.val && dfs(left.left, right.right) && dfs(left.right, right.left);
       }
   }
   ```

### 后记

从三轮面试情况来看，面试官随着级别的不同，问的问题也约偏架构，但是算法永远是不变的一个点。建议大家刷刷LeetCode。

整个秋招我面试了国内很多的互联网公司，经历的面试大概有30+场，在接下来的日子里，我会把这些笔记慢慢发布出来，供大家准备春招和实习。其实大约三个月没有面试了，上面这些问题我都有些不知道了，所以还是告诫我们，要持续学习！

其实后续我计划把我的面试帖子整理成PDF，大概分为面试步骤、常见面试题、我的面试经历、必刷算法、OFFER选择四个模块。希望不会咕咕