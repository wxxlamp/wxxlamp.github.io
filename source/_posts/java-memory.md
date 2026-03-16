---
title: "类在内存中的存储方式"
tags:
   - Java
   - Jvm
categories:
   - 基础夯实
date: 2020-12-17 10:36
description: "本文系统梳理Java内存结构，从C与Java的内存处理方式差异切入，详解JDK8中程序计数器、虚拟机栈、本地方法栈、堆与方法区（含运行时常量池）的职责与特点。通过具体代码演示类加载、初始化、运行各阶段的内存分配过程，并深入讲解父类继承、接口实现、内部类、不规则数组等场景的内存逻辑模型，以及基本数据类型在栈与堆上的分配规则。"
---

Java有许多特点，如线程并发，类加载，垃圾回收，语法糖，丰富的官方类库，易懂的面向对象设计，平台兼容等等。对于内存来说，从宏观上，主要分为静态和动态两部分，静态的是内存的空间结构，动态的是内存的分配和回收。本篇文章，就来总结一下Java中的内存结构。

### 1. 语言间的内存差异

相对于C来说，在对内存的处理方式上，Java做了两点不同的决策。

#### 1.2 内存的空间结构

对于C来说，程序员会以系统的视角去看内存——一块连续的字节数组。一个C程序最起码是一个进程，它会直接映射到操作系统对进程的空间分配中，如程序块和数据，用户栈，运行堆，共享库以及用户无法访问的内核虚拟内存。一个简单的`HelloWorld.c`程序，它的代码会存放到程序块区域，静态变量会存放到数据区，当调用函数时，会把函数地址和变量压入用户栈中，当使用malloc分配空间时，数据会存放在运行堆中。

对于Java来说，VM会对内存再进行一次抽象和封装。它把内存分为线程独有的程序计数器、虚拟机栈、本地方法栈和线程共享的堆以及方法区(其实方法区也是堆)。当程序new一个对象后，对象的实例会被存放到堆中，对象的信息和方法以及静态变量会被存放到方法区中。

总结来说，C语言中，程序员可以访问的内存单位是字节数组；而Java语言中，程序员可以访问的内存单位是抽象出来的对象。因为寄存器可以访问的内存单位也是字节数组，这说明使用C语言的程序员可以直接访问底层，进行更多操作，这也是C语言程序员鄙视Java程序员的一个重要原因之一。但是访问的更多不仅仅意味着权利，也以为着责任，因为没有对象级的抽象，导致了C程序尤其是大型程序会莫名奇妙的抛出缓冲区溢出，数组越界，乱码等等难以找到根源的问题。

#### 1.2 内存的分配回收

对于C来说，程序员需要主动去申请和释放内存。而对于Java来说，因为有了VM的存在，GC会自动回收不可达的对象。但是同时GC线程在回收垃圾的时候会造成STW（Stop the world），拖慢程序的性能。而且，因为对象交给了VM来负责清除，那么对象的清除时间其实是不可预测的。相对来说，C程序员可以完全操控内存的分配和回收时间，可以完全掌握内存的信息，这点是Java程序员做不到的。但是，如果C程序中忘记`free`内存空间，也将会造成不可估量的损失。

从内存处理的方式来看，C程序有着不容置疑的对内存完全掌控的能力，而对Java程序来说，因为VM做了一层抽象后，Java程序把内存的操作交给了VM来处理，变成了间接访问。同时，因为有了VM，Java程序可以随心所欲的编写代码而不用担心出现很大的BUG，这导致了Java语言极易上手，Java程序员良莠不齐，一直被行业诟病。

### 2. Java中的内存结构

Java的内存结构几乎是面试必问的一个问题，所以这里再拉出来回顾一下。

> 以下内存结构针对JDK8

#### 2.1 基本概念

* **虚拟机栈**：线程私有，每个方法非native方法对应一个栈帧，栈帧中包括局部变量表(以slot为基本单位，存储方法参数和内部变量)，操作数栈（存储计算参数和结果），动态链接等
* **本地方法栈**：线程私有，负责native方法
* **程序计数器**：线程私有，记录某个线程的字节码执行位置
* **堆**：线程共有，用来存放实例，是Jvm最大的一块区域，也是GC管理的主要区域。在JDK7及以前，分为新生代*( Eden 8、From Survivor 1、To Survivor 1 )*，老年代。新生代与老年代是1:2
* **方法区**：存储类的结构信息，除了运行时常量池，其他的都在MetaSpace中放着
  1. 运行时常量池，运行时将常量池的数据放入这里，同时包括字符串常量池，这个实际是在堆中放着，可以动态变化（如`String#intern()`）
  2. 常量池，存放编译期生成的字面量（文本字符串、八种基本类型的值、被声明为final的常量）以及符号引用（类和方法的全限定名、字段的名称和描述符、方法的名称和描述符），大小在运行期前已知。以类为单位
  3. 方法字节码，存放的是各个方法的字节码（依赖操作数栈和局部变量表，由JVM解释执行）

理论知识可以参考 [Bleem1](https://mritd.com/2006/01/02/java-memory-overview-of-vm-memory-auto-management-and-memory-regions/)、[Bleem2](https://mritd.com/2006/01/02/java-memory-method-area-and-runtime-constant-pool/)、[Bleem3]()

#### 2.2 程序演示

对于一个类来说，它主要分为两部分，分别是属性和方法。这两部分和我们计算机基础中的数据结构和算法是一一对应的。对于C程序来说，数据结构存放在堆中，算法存放在代码块中。下面，我们通过一个程序来说明Java程序的这两部分分别存放在哪里？

> 分配情况不考虑TLAB，JIT，逃逸分析等，同时也不考虑Eden和Survivor这些区域

```java
class MemoryStructTest {
    private static final String HELLO_WORLD = "hello world!";
    public static void main(String... args) {
        String helloWorld = HELLO_WORLD;
        System.out.print(helloWorld);
    }
}
```

当该程序被编译、类加载、初始化和运行时，这个程序在内存中是什么样子的呢？

* `MemoryStructTest`这个类的信息在类加载之后会被存储到方法区中。其中，包括Field，Method，常量池，static变量，类名等
* 类加载的最后一步初始化会去初始化static变量`HELLO_WORLD`，此时会去对String类进行类加载，`String`类会被按照刚才的方式类加载进入方法区，然后`HELLO_WORLD`这个字符串的引用会被字符串常量池中，而它真正被存在了堆中。而`helloworld`这个本地变量则是存在了虚拟机栈中了。
* 在运行之后，之前常量池的部分内容会被拷贝到运行时常量池中，同时，该类的然后VM开始逐行解释执行方法区`main`方法的字节码
* 当调用到第五行的时候，会对`System.out`这个类类加载到方法区，之后调用方法区中的静态方法，打印`helloWorld`这个本地变量

可以得到下图：

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/520f416a_java-memory-1.png)

有一点需要注意的是，对于String和基本类型，如果不主动new，它们会在常量池中，如果主动new，则会产生在堆中

### 3. 具体类型的存储格式

#### 3.1 父类的存储格式

这个是我大二时候画的一个内存图，现在看来，还是有些东西的，再次放上来：

```java
class A {
    //产生新的虚(virtual)方法MethodVirtual(),new slot
    void  MethodVirtual() {
        System.out.println("aV");
    }
    //产生新的虚(virtual)方法MethodVirtual1,new slot
    void  MethodVirtual1(){
        System.out.println("aV1");
    }

}
class B extends A {
    // 覆盖父类的MethodVirtual()方法，reuse slot
    @Override
    void  MethodVirtual() {
        System.out.println("bV");
    }
    // 覆盖父类的MethodVirtual1()方法，reuse slot
    @Override
    void  MethodVirtual1()	{
        System.out.println("bV1");
    }
}
class C extends B {

}
class D extends C {
    // 覆盖MethodVirtual()方法
    @Override
    void MethodVirtual() {
        System.out.println("dV");
    }

    // 覆盖MethodVirtual()1方法
    @Override
    void  MethodVirtual1() {
        System.out.println("dV1");
    }
}
public class A_Polymorphism {
    public static void main(String[] args) {

        A a;
        B b;
        C c;
        D d;

        a = new A();
        b = new B();
        c = new C();
        d = new D();

        A ab = b;
        A ac = c;
        A ad = d;

        B bc = c;
        B bd = d;

        C cd = d;


        System.out.println("--------------------方法多态---------------------------");

        System.out.println("--------------------a.MethodVirtual()---------------------------");
        a.MethodVirtual();
        ab.MethodVirtual();
        ac.MethodVirtual();
        ad.MethodVirtual();

        System.out.println("--------------------a.MethodVirtual1()---------------------------");
        a.MethodVirtual1();
        ab.MethodVirtual1();
        ac.MethodVirtual1();
        ad.MethodVirtual1();

        System.out.println("--------------------b.MethodVirtual()---------------------------");
        b.MethodVirtual();
        bc.MethodVirtual();
        bd.MethodVirtual();

        System.out.println("--------------------b.MethodVirtual1()---------------------------");
        b.MethodVirtual1();
        bc.MethodVirtual1();
        bd.MethodVirtual1();

        System.out.println("--------------------c.MethodVirtual()---------------------------");
        c.MethodVirtual();
        cd.MethodVirtual();

        System.out.println("--------------------c.MethodVirtual1()---------------------------");
        c.MethodVirtual1();
        cd.MethodVirtual1();

        System.out.println("--------------------d.MethodVirtual()---------------------------");
        d.MethodVirtual();

        System.out.println("--------------------d.MethodVirtual1()---------------------------");
        //d = null;
        d.MethodVirtual1();
    }
}
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/20190815120936937.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NvZGVyX3doYXQ=,size_16,color_FFFFFF,t_70)

#### 3.2 接口的存储格式

```java
interface I {
    void func1();
}
class o {
    void func(){
        System.out.println("you can hit me");
    }
}
class c extends o implements I {
    public void func1() {
        System.out.println("Stonee is so handsome");
    }
    void func2(){
        System.out.println("you can't hit me because the interface don't have me");
    }
}public class Test {
    public static void main(String [] args){
        //inerface
        I ic = new c();
        ic.func1(); //ok
        //a.func2(); //no
        ((c) ic).func2(); //ok
        ((c) ic).func(); //ok

        //class parents
        o oc = new c();
        oc.func();
        ((c) oc).func1();
        ((c) oc).func2();

        //class son
        c cc = new c();
        cc.func1();
        cc.func2();
        cc.func();

        o oo = new o();
        oo.func();
    }
}
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/20190411183056417.PNG?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NvZGVyX3doYXQ=,size_16,color_FFFFFF,t_70)

> PS：上面的 “堆·类” 应该改为方法区

#### 3.3 内部类的存储格式

内部类通过语法糖会被解析为一个普通的类，然后和上边是一样的

#### 3.4 数组的存储格式

在Java中，数组也是一个对象，这样的抽象，极大程度上保证了对数组操作的安全性，不会产生C程序中的数组越界时内存覆盖的问题。

一个包含数组，接口，类以及继承的程序：

> **声明：本程序完全是为了演示接口，类等的内存逻辑模型的demo** 
> **另：此程序有点冗余，但确实可以说明继承关系，而且内存逻辑模型是用手画的，只画了一些重要部分，没有上面程序画的详细**

```java
package chapter06;
/**
* 关于接口和类的继承以及不规则数组的内存逻辑模型
* @version 1.0 2019-4-8
* @author Stonee(http://www.stonee.club)
*/
public class InterfaceTestCourse {
    public static void main(String [] args){

    healthPigeon [][] a = new healthPigeon[2][];
    a[0] = new healthPigeon[1];
    a[1] = new healthPigeon[2];

    for (healthPigeon[] e:
        a) {
        for (healthPigeon es:
            e) {
            es = new healthPigeon();    //一定要先对数组赋值，不然会指向null，然后报错
            System.out.println();
            es.eat();
            es.move();
            es.breathe();
            es.feather();
            es.fly();
            es.fxxk();
            System.out.println();
            }
         }
    }
 }
 // 定义接口
 // 定义父接口
interface canEat {
    void eat();     //默认修饰符为 public abstract
    default void fxxk(){
        System.out.println("I like eat");
    }
}
interface canMove {
    void move();
    default void fxxk(){
        System.out.println("I like move");
    }
}
interface canFly{
    void fly(); // 子类已经重载，为什么说此方法未被调用？
}
interface canBreathe{
    void  breathe();
}// 定义子接口
interface bird extends canBreathe,canFly{
    void feather();
 }
 // 定义类
 // 定义父类
 class pigeon implements bird{
    @Override
    public void feather() {
        System.out.println("The pigeon have feather");
    }
    @Override
    public void breathe() {
        System.out.println("The pigeon can breathe");
     }
    @Override
    public void fly() {
        System.out.println("The pigeon can fly");
    }
 }
 // 定义子类
class healthPigeon extends pigeon implements canEat,canMove{
    @Override
    public void eat() {
        System.out.println("The cute Pigeon can eat");
    }
    @Override
    public void move() {
        System.out.println("The cute pigeon can move");
    }
    public void fxxk(){
        canEat.fxxk();  //此处必须声明调用接口的哪个默认方法
    }
}
```
<img src = "https://img-blog.csdnimg.cn/2019041118341719.jpg" style="transform:rotate(270deg)"/>

#### 3.5 基本数据类型的存储格式

对于基本数据类型来说，如果是局部变量，则直接回按照字节规范分配到栈上。如果是类的全局变量，则随着实例的初始化分配到堆上。

如果类实例的某个属性是另外个实例，那么会有指针指向另外个实例。而如果属性是基本类型的话，则没有指向，直接分配这个这么大字节的空间

> 附基本类型的字节：byte 1 字节，char 2 字节，short 2 字节，int 4 字节，float 4 字节， long 8 字节， double 8 字节，boolean 不确定


### 4. 后记

其实这些东西我在去年的这个时候都已经知道了，但是没有一个贯通的概念，今天一总结，才有种豁然开朗的感觉。

但是，了解的越多，才发现在不懂的越多，加油吧



> 无论高级语言提供多么优美的数据模型，编译成机器代码之后，它只是简单地将内存理解为一个很大的，按照字节(8bits)寻址的数组。而机器访问内存，则都是通过地址来访问的
>
> 32位机器和64位机器有什么不同呢？就是说的地址总线，32位机器表明程序的地址可以占用4个字节，能够访问的地址有4GB。而64位则表明程序的地址可以占8个字节，能够访问2^64byte



