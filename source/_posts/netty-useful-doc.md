---
title: "Netty可用性剖析"
date: 2023-01-10 10:36
tags:
   - Netty
categories:
   - 面试经验
description: "剖析Netty框架核心优势：三层逻辑架构、Bootstrap脚手架、Handler责任链、TCP粘包拆包解决方案、ByteBuf动态扩缩容与序列化支持。"
---

Netty使用起来非常简单，不用像写Java原生的NIO一样， 各种Select的监听和处理；同时，也无需处理Java NIO自身的各种BUG；以及网络编程中的各种坑，如TCP的沾包拆包问题等。
同时，各种网络协议也是网络编程的复杂之一，Netty也会帮助我们处理各种疑难问题。
下面我们来具体分析：

## Netty的系统架构
Netty从逻辑架构上可以分为三层，分别是通信层，职责链层和业务层。通信层负责通信处理；责任链层负责不同节点的编排，同时还会处理基础的逻辑，如编解码，POJO对象转换，心跳发送等等；而业务层就是单纯的负责上层业务的开发处理

![Netty架构图](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/1dc0a526_netty-useful-doc-1.png)

其中，三层的主要分工如下：
**通信层**：该层主要包含NioSocketChannel和NioServerSocketChannel用来和Socket的连接，通过Reactor模型来处理高并发请求。该层的主要职责是监听网络的读写和连接操作，负责将网络层的数据读取到内存缓冲区中，然后出发各种网络事件，例如连接，读/写等事件，将这些事件触发到pipeline中，由pipeline来进行后续处理。
**职责链层**：它负责事件在职责链中的有序传播，同时负责动态地编排职责链。通过不同的Handler来处理不同的基础情况，譬如，编解码处理器，POJO 对象转换器，粘包拆包处理器，心跳发送器，权限验证器等，这样上层业务则只需要关心处理业务逻辑即可，不需要感知底层的协议差异和线程模型差异，实现了架构层面的分层隔离。
**业务层**：业务逻辑编排层通常有两类：一类是纯粹的业务逻辑编排，还有一类是其他的应用层协议插件，用于特定协议相关的会话和链路管理。

## 易用的脚手架
### Java原生IO
Java的原生IO编写起来是十分复杂的，而且Java的BIO和NIO的编写方案也完全不相同，如果一个项目刚开始为了图省事使用的是BIO，当项目业务量起来之后，如果也切换到NIO，就会十分痛苦。同时Java原生的NIO，处理起来也非常麻烦，需要感知许多select的事件，同时需要自己分配线程去处理业务逻辑
#### BIO
伪代码如下：
```java
public class BioServer {
    public void run() {
        try(ServerSocket server = new ServerSocket(1234)) {
            //创建服务器
            System.out.println("服务器已启动……");
            //循环等待连接多个客户端
            while (true) {
                Socket socket = server.accept();
                // 读取输入流
                try(BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                    PrintWriter out = new PrintWriter(socket.getOutputStream(), true)) {
                    String body;
                    body = in.readLine();
                    out.println(body);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
	}
}
```
#### NIO
伪代码如下：
```java
public class NioServer {

    public void run() {
        try {
            // 开启多路复用器
            Selector selector = Selector.open();
            // 开启服务器
            ServerSocketChannel serverSocketChannel = ServerSocketChannel.open();
            serverSocketChannel.socket().bind(new InetSocketAddress(1234));
            System.out.println("服务器已启动……");
            // 设置服务器非阻塞
            serverSocketChannel.configureBlocking(false);
            // 将ServerSocketChannel注册到Selector上，监听 OP_ACCEPT 事件
            serverSocketChannel.register(selector, SelectionKey.OP_ACCEPT);
            while (true) {
                int select = selector.select();
                // 当有事件发生的时候，处理事件
                if (select > 0) {
                    Set<SelectionKey> selectionKeys = selector.selectedKeys();
                    for (SelectionKey selectionKey : selectionKeys) {
                        // 如果是连接事件
                        if (selectionKey.isAcceptable()) {
                            ServerSocketChannel serverSocket = (ServerSocketChannel) selectionKey.channel();
                            // 接收客户端连接，并且设置非阻塞，然后注册SocketChannel到多路复用器上，监听读事件
                            SocketChannel socketChannel = serverSocket.accept();
                            System.out.println(socketChannel.getRemoteAddress() + "已连接");
                            socketChannel.configureBlocking(false);
                            socketChannel.register(selector, SelectionKey.OP_READ);
                        } else if (selectionKey.isReadable()) {
                            // 如果有可读事件，那么处理数据
                            SocketChannel socketChannel = (SocketChannel) selectionKey.channel();
                            ByteBuffer byteBuffer = ByteBuffer.allocate(1024);
                            int read = socketChannel.read(byteBuffer);
                            if (read > 0) {
                                String msg = new String(byteBuffer.array(), StandardCharsets.UTF_8);
                                System.out.println(socketChannel.getRemoteAddress() + ":" + msg);
                            } else if (read == -1) {
                                socketChannel.close();
                                System.out.println(socketChannel.getLocalAddress() + "断开连接");
                            }
                        }
                    }
                }
            }
        } catch (IOException e) {

        }
    }
}
```
### Netty的Bootstrap
Netty通过自己的脚手架Bootstrap解决了上面的问题，通过Bootstrap，我们可以轻松的选择NIO还是BIO，选择线程模型，选择绑定的端口以及对应的业务逻辑处理器
如下面代码所示：
```java
public static void main(String[] args) {
    EventLoopGroup bossGroup = new NioEventLoopGroup();
    EventLoopGroup workerGroup = new NioEventLoopGroup();
    try {
        ServerBootstrap serverBootstrap = new ServerBootstrap();
        serverBootstrap.group(bossGroup, workerGroup)
                // channel fact
                .channel(NioServerSocketChannel.class)
                // 服务端 accept 队列的大小
                .option(ChannelOption.SO_BACKLOG, 1024)
                // TCP Keepalive 机制，实现 TCP 层级的心跳保活功能
                .childOption(ChannelOption.SO_KEEPALIVE, true)
                // 允许较小的数据包的发送，降低延迟
                .childOption(ChannelOption.TCP_NODELAY, true)
                .childHandler(new ChildChannelHandler());
        ChannelFuture f = serverBootstrap.bind(1234).sync();
        // 绑定端口，并同步等待成功，即启动服务端
        if (f.isSuccess()) {
            LOGGER.info("[start][Netty Server 启动在 {} 端口]", 1234);
        }
    } catch (InterruptedException e) {
        throw new RuntimeException(e);
    }
}
```
## 基于事件的过滤器模式
Netty的很多逻辑处理都是基于过滤器模式的，如下所示：
![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/c19b08d3_netty-useful-doc-2.png)
当一个请求进入Netty之后，Netty会把该请求封装成对应的channel，然后将该channel以过滤器模型的方式在pipeline中流转。在流转的过程中，该channel会经历不同的Handler，这些handler有负责编解码的，也有负责不同业务自定义处理的等等，当所有Handler都执行完了之后，就会将结果的报文返回给调用方。
可以看出，通过过滤器模式，Netty的不同Handler之间实现解耦，翻开Netty的源码我们就能发现，Netty内置了很多Handler来做报文的组装和拦截。当业务有自定义的逻辑的时候，直接新增Handler即可，完全解耦，不会对其他逻辑造成影响

## TCP流导致上层粘包和拆包问题
### 粘拆包原因
在TCP/IP网络模型中，因为TCP协议在传输层，主要是对数据进行打包传输的，它并没有能力区分业务层的报文段（如基于TCP的HTTP协议等），参考Netty官网的文档：
> In a stream-based transport such as TCP/IP, received data is stored into a socket receive buffer. Unfortunately, the buffer of a stream-based transport is not a queue of packets but a queue of bytes. It means, **even if you sent two messages as two independent packets, an operating system will not treat them as two messages but as just a bunch of bytes**. Therefore, there is no guarantee that what you read is exactly what your remote peer wrote

通俗来说，就是send和recv其实是根据以字节为单位传输的，同时，对于TCP协议来讲，因为TCP会根据滑动窗口弹性的发送不同长度的字节数，导致上层协议没有办法区分到底发送完没有。
本质上说，TCP是不存在粘包和拆包的，因为TCP协议根本没有“包”这个概念，粘包和拆包，也不能说是TCP协议的问题，这本来就是需要应用层自己解决的事情。
举个例子：
![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/da729e4d_netty-useful-doc-3.png)
从上面的图中，我们可以看到，正常的业务报文应该是msg1（包含byte1和byte2），msg2（包含byte3和byte4），但是因为TCP是根据byte发的，所以就很有可能发成msg1(byte1)，msg2（byte2&byte3&byte4），这样就会导致我们所说的粘包和拆包问题
所以，针对TCP的粘包和拆包问题，是网络编程中一个必须要解决的问题。

### 解决方案
对于粘包和拆包问题，一般都是对包的格式进行约束，常见的解决方案有四种：

- 将业务层协议包的长度固定下来，每个包都固定长度，比如512个字节大小，如果客户端发送的数据长度不足512个字节，则通过补充空格的方式补全到指定长度；
- 在每个包的末尾使用固定的分隔符，如换行符/n，如果一个包被拆分了，则等待下一个包发送过来之后找到其中的\n，然后对其拆分后的头部部分与前一个包的剩余部分进行合并即可；
- 仿照TCP/IP协议栈，将消息分为head和body，在head中保存有当前整个消息的长度，只有在读取到足够长度的消息之后才算是读到了一个完整的消息；
- 通过自定义协议进行粘包和拆包的处理。


### Netty的解决之道

对于Netty来说，它的解决方案理念和刚才梳理的是一样的，不过Netty把这些解决方案融入到了自己的代码库中，我们可以基于Handler，直接开箱即用，如下所示：

1. 按照换行符切割报文：LineBasedFrameDecoder
2. 按照自定义分隔符符号切割报文：DelimiterBasedFrameDecoder 
3. 按照固定长度切割报文：FixedLenghtFrameDecoder

这些解决方案全被封装到了handler中，我们可以基于Netty的责任链模式，进行如下调用即可：
```java
serverBootstrap.group(bossGroup, workerGroup)
    // channel fact
    .channel(NioServerSocketChannel.class)
    .childHandler(new ChannelInitializer<SocketChannel>() {
        @Override
        public void initChannel(SocketChannel ch) {
            ch.pipeline.addLast(new FixedLenghtFrameDecoder());
        }
    }
);
```
## 易用的Buffer
在网络编程中，基本都是基于TCP报文的字节流的操作，所以Java的NIO又新增了ByteBuffer，只不过Java原生的ByteBuffer，非常难操作，也不能扩缩容，所以Netty又重新封装了自己的Bytebuf，除了性能上的优势之外，Netty的Buffer在使用上相对于NIO也非常简洁，有如下特点：
### 动态扩缩容
顾名思义，Netty中的ByteBuffer可以像Java中的ArrayList一样，根据写入数据的字节数量，自动扩容。代码如下所示：
```java
final void ensureWritable0(int minWritableBytes) {
    final int writerIndex = writerIndex();
    final int targetCapacity = writerIndex + minWritableBytes;
    // using non-short-circuit & to reduce branching - this is a hot path and targetCapacity should rarely overflow
    if (targetCapacity >= 0 & targetCapacity <= capacity()) {
        ensureAccessible();
        return;
    }
    if (checkBounds && (targetCapacity < 0 || targetCapacity > maxCapacity)) {
        ensureAccessible();
        throw new IndexOutOfBoundsException(String.format(
                "writerIndex(%d) + minWritableBytes(%d) exceeds maxCapacity(%d): %s",
                writerIndex, minWritableBytes, maxCapacity, this));
    }

    // Normalize the target capacity to the power of 2.
    final int fastWritable = maxFastWritableBytes();
    int newCapacity = fastWritable >= minWritableBytes ? writerIndex + fastWritable
            : alloc().calculateNewCapacity(targetCapacity, maxCapacity);

    // Adjust to the new capacity. 【此处进行扩容】
    capacity(newCapacity);
}
```
这个在编写代码的时候，满足ByteBuf最大缓冲区的情况下，我们可以毫无顾忌地调用#write方法增加字节，而不用手动去check容量满足，然后去重新申请
### 读写指针代替#filp
#### 原生ByteBuffer的弊端
Java原生的ByteBuffer的数据结构，分为limit，capacity两个指针，如果我们写入“Hollis”之后，ByteBuffer的内容如下：
![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/7bde4ed9_netty-useful-doc-4.png)
此时，如果我们要从该ByteBuffer中read数据，ByteBuffer会默认从position开始读，这样就什么也读不到，所以我们必须调用#filp方法，将position指针移动，如下：
![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/342339d7_netty-useful-doc-5.png)
这样我们才可以读到“Hollis”这个数据，万一我们调用的时候忘记使用filp，就会很坑爹。

#### Netty的ByteBuf
Netty自带的ByteBuf通过读写双指针避免了上面的问题，假如我们写入“Hollis”后，ByteBuf的内容如下：
![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/5e63d65f_netty-useful-doc-6.png)
在写入的同时，我们可以直接通过readPointer读取数据，如下所示：
![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/712bcc14_netty-useful-doc-7.png)
在这个过程中，我们完全不用像JavaNIO的ByteBufer一样，感知其结构内部的操作，也不用调用filp，随意的读取和写入即可。
同时，假如我们读Hollis这个数据，读到了一半，还剩下“is”没有读完，我们可以调用discardReadBytes方法将指针移位，为可写区域增加空间，如下所示：
![image.png](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/ade22650_netty-useful-doc-8.png)

### 多种ByteBuf实现
Netty根据不同的场景，有不同的ByteBuf实现，主要的几种分别是：Pooled，UnPooled，Direct，Heap，列表格如下：

|  | Pooled | UnPooled |
| --- | --- | --- |
| HeapByteBuf | 业务处理使用+高并发 | 业务处理使用+正常流量 |
| DireactByteBuf | Socket相关操作使用+高并发 | Socket相关操作使用+正常流量 |

当然Netty中的Buffer性能相比于Java NIO的Buffer也更强，譬如我们熟知的Zero-Copy等，这个我们放到性能篇中剖析
## 多种序列化方案
在网络编程中，是一定少不了序列化的，当我们在内存中形成对象之后，需要将对象转换为字节流通过Socket输出到网络中，同时接收端还需要通过Socket接收到字节流之后将字节转为内存中的对象，但是我们知道，Java原生的序列化方案不仅耗时长，而且转化出来的字节，占用内存也大，导致网络的吞吐量很高，同时，它也无法跨语言。所以，对于网络编程来讲，我们亟需要通过其他优秀的序列化方案进行网络传输。
Netty内置了很多序列化方案，如比较著名的Google的ProtoBuf，Netty就通过了io.netty.handler.codec.protobuf包下的类对其进行了支持。

## Reference

1. [Netty Doc](https://netty.io/3.8/guide/#preface.2)
2. [Netty权威指南](https://stream.nosdn.127.net/kids/1625672349182/Netty%E6%9D%83%E5%A8%81%E6%8C%87%E5%8D%97.pdf)
