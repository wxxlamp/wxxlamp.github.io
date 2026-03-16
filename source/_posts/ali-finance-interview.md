---
title: "阿里企业金融实习面试"
date: 2020-04-03 10:36
tags:
   - Java
   - Internships
categories:
   - 面试经验
description: "阿里企业金融实习五轮面试复盘，涵盖Java并发、Spring原理、MySQL、Redis、MQ等技术点，及多线程编程题，分享面试经历与最终选择。"
---

面试流程是p7 -> p8 -> p9 -> p9（交叉）-> HR
最终还是选择了这个BU去实习，希望能有一个 好结果

<!-- more -->

## 一面
### Java

#### 1. HashMap和ConcurrentHashMap

> ConcurrentHashMap如何保证并发

#### 2. 线程进程和协程

#### 3. 线程通信方式

semphore，wait/notify，condition

#### 4. BIO，NIO，AIO

> NIO的几种实现方式

#### 5. Jvm结构和GC

#### 6. OOM

## 框架

#### 7. Spring对bean的管理

* 采用工厂模式的IOC容器

* 两个接口ApplicationContext和BeanFactory

  * BeanFactory采取的懒加载的方式,在获取对象时才会实例化

  * ApplicationContext会在工厂初始化时立即实例化对象

  * BeanFactory作为顶级接口主要面向于Spring框架本身,仅提供了基础基本的容器功能如DI

  * ApplicationContext,是BeanFactory的子接口,意味着功能比BeanFactory更多,诸如国际化,注解配置,XML配置等等,因此ApplicationContext使用更多

    - ApplicationContext的两个实现类区别:
    - ClassPath表示从类路径中获取配置文件;

    - FileSystem表示从文件系统获取配置文件

* SpringBean的生命周期

* Bean的依赖注入等等

[Bean管理](https://www.cnblogs.com/yangyuanhu/p/12164380.html)

#### 8. Spring AOP

面向切面编程

#### 9. 动态代理和Cglib的区别

平行和继承

### 设计模式

#### 10. 观察者模式

这个题大概是说实现一个售票系统，要求出一个人之后才能进一个人。我刚开始说的是阻塞队列，即生产者消费者模式。然后面试官让我说一个设计模式，这就肯定是观察者模式了

### 数据库

#### 11. ACID

#### 12. 隔离级别

#### 13. 索引设计，组合索引

#### 14. Redis的主从复制和哨兵机制

在主从复制模式中，主机宕机后salve会立刻补上（人工），复制是基于rdb的。主要用于读写分离和容灾备份。如果master恢复，则投票选取

哨兵模式中，从机会定时向master发送ping命令

### 项目

#### 15. 博客系统如何做到实时评论

有三种实现方式，短轮询，长轮询和长连接

#### 16. 项目的难点在哪里

这种题说简单也简单，因为可以有我们自己去引导面试官，但是说难也难，因为可能不知不觉中我们就给自己挖坑了。

#### 17. Consumer接收到消息后没来得及消费MQ挂掉怎么办

Consumer自身维护一个持久化的offset（对应MessageQueue里面的min offset），标记已经成功消费或者已经成功发回到broker的消息下标，因为offset是持久化的，所以挂掉之后也没有影响

[挂掉怎么办](https://blog.csdn.net/yueloveme/article/details/98208486)

#### 18. Redis挂掉怎么办

在对redis操作时，要check redis是否可用，如果不可用直接抛异常，如果

### 算法题

#### 19. LeetCode 58 

这个是easy级别的，有两种方式，第一种通过split切分，然后逆序输出，第二种翻转所有字符串，然后再翻转每个单词

## 二面

### Java

这次竟然没有一个Java基础相关的。。。。

我极度怀疑面试官看了我博客，故意避开我会的。。。

### 框架

#### 1. @bean的作用

声明该返回值是一个bean

**运行还是编译** 运行

**bean如何起作用** 

通过@ComponentScan对包进行扫描

**通过什么查看注解**

反射有个查看annotation方法

####  2. 为什么@Before可以AOP

在spring的生命周期的后置方法中，先查找实现了pointcutAdvisor的切面类，该类包含了Pointcut和Advice对象，检查在Pointcut中的表达式能否匹配到当前的bean类，如果匹配则对bean进行织如

**代理类没有接口怎么办** cglib

**如何代理final** 通过aspectJ或者动态代理

#### 3. SpringBoot的@SpringBootApplication

有三个nb注解@EnableAutoConfiguration，@ComponentScan和@SpringBootConfiguration，第一个里面会有一个@Import注解，导入一个Select.class，该class会通过拿到每一个starter里面的resources/META-INF的文件

**如何写一个starter**

在自定义的starter里面增加一个spring.proprites文件用来通知SpringBoot配置类的位置，然后在配置类中注入bean，如果需要映射参数的时候，可以通过@ConfigurationProperties注解

[SpringBootStarter](https://www.cnblogs.com/yuansc/p/9088212.html)

### DB

#### 4. 为什么索引用B+树

深度浅，每个节点的key值更多

#### 5. 为什么只有右模糊查询走索引

用B+树来解释，MySQL的B+树索引是按照从左向右的原则进行匹配的，如果其他模糊效率将是index

### 网络

#### 6. 面试时语音走得所有协议

**语音如何通过网络传输**

**微信文字的传输**

**微信发文字和图片传输的区别**

反正没有回答到点上，有知道的logo可以发消息给我

### 算法

#### 7. 了解哪些数据结构和算法

dp，贪心，dfs，bfs，prime，kruskal，树，栈，图，链表，数组，字符串

**堆排序是稳定的吗** 不稳定

**堆排序的最终结果集是平衡二叉树吗** 不是

**Arrays.sort()源码**

有三种排序方式：双轴快排，并发归并，以及修改的归并

主要是修改的归并：如果长度小于7的话会使用插入排序（即将删除）

另外一种修改的归并排序是TimSort：

1. 扫描数组，确定其中的单调上升段和严格单调下降段，将严格下降段反转；

2. 定义最小基本片段长度，短于此的单调片段通过插入排序集中为长于此的段；

3. 反复归并一些相邻片段，过程中避免归并长度相差很大的片段，直至整个排序完成，所用分段选择策略可以保证O(n log n)时间复杂性。 

可以看到，原则上TimSort是归并排序，但小片段的合并中用了插入排序。TimSort的最好复杂度是O(N),但是普通规并是O(nlogn)

[TimSort](https://www.jianshu.com/p/892ebd063ad9)

### OS

#### 8. .java文件如何被OS执行

我回答的是虚拟机的那一块

### 项目

#### 9. 如何提高并发量

集群，缓存，数据库

#### 10. 如何保证数据一致性

加锁，双删，MQ

### 做题

面试官说给我个不常见的题，我吐。。。

#### 11. 请用JAVA代码完成以下功能，要求使用多线程

`cat /home/admin/logs/*.log | grep "Login"| sort -nr | uniq -c`

```java
/**
 * 读取 这个文件夹下 以.log结尾的文件
 * 匹配包含Login的字符串
 * 并将字符串逆序排列相同的字符串合在一起
 * 并在左侧标出重复出现的次数
 *
 * @author wxxlamp
 * @date 2020/03/11~14:53
 */
public class Ali {
    public static String dir = "/home/admin/logs/";
    public static String target = "Login";

    public static void run() throws ExecutionException, InterruptedException {
        Tree tree = new Tree();
        List<String> stringList = getMultiFile(dir);
        for (String s : stringList) {
            tree.add(s);
        }
        tree.print();
    }

    private List<String> getMultiFile(String dir) throws ExecutionException, InterruptedException {
        File fileDir = new File(dir);
        File[] files = fileDir.listFiles();
        List<String> list = new ArrayList<>();
        assert files != null;
        for (File file : files) {
            if (file.getName().matches("^((?!log).*).log$")) {
                FutureTask<List<String>> futureTask = new FutureTask<>(new Worker(file));
                new Thread(futureTask).start();
                list.addAll(futureTask.get());
            }
        }
        return list;
    }

    private List<String> getTargetStringLine(File file) {
        Charset charset = StandardCharsets.UTF_8;
        StringBuilder sb = new StringBuilder();
        try(FileChannel fin = new FileInputStream(file).getChannel()) {
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            while (fin.read(buffer) != -1) {
                buffer.flip();
                sb.append(charset.decode(buffer));
                buffer.clear();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        String[] ss = sb.toString().split("\\r");
        List<String> stringList = new ArrayList<>();
        for (String s : ss) {
            if (s.contains(target)) {
                stringList.add(s);
            }
        }
        return stringList;
    }

    private class Worker implements Callable<List<String>> {
        private File file;
        public Worker (File file){
            this.file = file;
        }

        @Override
        public List<String> call() {
            return getTargetStringLine(file);
        }
    }
    
    private static class Tree {

        private Map<String,Integer> map = new TreeMap<>(
                Comparator.reverseOrder());

        public synchronized void add(String str) {
            if(!map.containsKey(str)) {
                map.put(str,1);
                return;
            }
            Integer num = map.get(str);
            map.put(str, ++num);
        }

        public void print() {
            print(map);
        }

        public void print(Map<String, Integer> map) {
            for (Map.Entry<String, Integer> entry : map.entrySet()) {
                System.out.println(entry.getKey() + " : " + entry.getValue());
            }
        }
    }
}

```

#### 12. LeetCode打家劫舍

#### 13. 写一个黑名单过滤系统

> 这两个算法题是淘宝一面后的笔试题，不是本次面试题

### 复盘

以前都是听说阿里越往后项目越多，为什么这次全是基础啊QAQ

突然发现面试官会看我CSDN，我在考虑要不要把我的面经设为私人可见，因为最近发现面试官问的问题基本刚好撇开了我整理的

这次的面试官和往常的大不一样，完全不走常规路，就像是和我讨论问题一样，一点一点问，完全问到我不会。还有一个就是写第一个场景题的时候，我多线程写完没来得及提交就到时间了，淦。这个场景题据我所知会成为最终评级考核的参考之一，我伤心555

面试官夸说我在本科生中还不错，对我印象挺好，但是还是要多实践。幸好二面险过。

## 三面

### Java

#### 1. 接触Java多久

#### 2. Java的学习方法

老师-视频-博客-文档-官方技术号

### 设计模式

#### 3. 熟悉哪些常用的设计模式

### DB

#### 4. MySQL的性能调优

redo log buffer加大，数据库连接池，索引优化相关

### 项目

#### 5. 项目的性能优化

堆缓存和MQ

#### 6. 秒杀系统的超买怎么解决



**有没有参考成熟的技术方案**

推荐美团和阿里的技术博客

#### 7. 秒杀系统的分工如何

**如何处理和同伴的技术争论**

#### 8. 整个项目做了多少时间

#### 9. 项目优化的空间

CDN，微服务

### 其他

#### 10. 如何安排自己的学习时间

#### 11. 为什么要在CSDN写博客

#### 12. 一般分享什么文章

#### 13. 有没有了解过新技术

docker，k8s，severless，severMesh，JDK8~14

#### 14. 个人的技术方向

#### 15. 对业务方面有什么需求

#### 16. 对前面几轮面试回答不好问题的反思

## 四面

1. 缓存一致性
2. mq的事物一致性
3. mq的两阶段提交
4. mq消息有序发送
5. 为什么这样保证？
6. GC机制
7. 可达性分析
8. RPC
9. 线程的状态
10. 线程阻塞和等待的区别
11. NIO
12. AOP如何实现
13. 代理模式？实现方式？
14. 比赛情况

## HR
1. 项目如果商用的话有哪些改进的点
2. 其他的忘了