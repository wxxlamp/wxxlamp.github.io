---
title: "Java Runtime Memory: Object Storage and Class Loading"
tags:
  - Java
  - Java 虚拟机
categories:
  - 基础夯实
date: 2020-12-17 10:36
description: >-
  A systematic overview of the Java memory structure, comparing C and Java
  memory handling, explaining the responsibilities of the JDK 8 virtual
  machine stack, heap, method area, and other regions, and illustrating class
  loading, memory allocation, and the memory model in inheritance and
  interface scenarios.
lang: en
translation_of: java-memory
---

Java has many features, such as multithreading, class loading, garbage collection, syntactic sugar, rich official class libraries, an easy-to-understand object-oriented design, and platform compatibility. From a memory perspective, it can be viewed at a high level as two parts: static and dynamic. The static part is the memory space structure, and the dynamic part is memory allocation and reclamation. This article summarizes the memory structure in Java.

### 1. Memory Differences Between Languages

Compared with C, Java makes two different decisions in how it handles memory.

#### 1.2 Memory Space Structure

For C, programmers view memory from the system's perspective: a continuous array of bytes. At minimum, a C program is a process, and it maps directly to the operating system's process-space allocation, including the program text and data, user stack, runtime heap, shared libraries, and kernel virtual memory that users cannot access. In a simple `HelloWorld.c` program, the code is stored in the text region, static variables are stored in the data region, function addresses and variables are pushed onto the user stack when a function is called, and data is stored in the runtime heap when `malloc` is used to allocate space.

For Java, the VM abstracts and encapsulates memory again. It divides memory into the thread-private program counter, virtual machine stack, native method stack, and the thread-shared heap and method area (in fact, the method area is also part of the heap). When a program creates an object with `new`, the object's instance is stored in the heap, and the object's information, methods, and static variables are stored in the method area.

In summary, in C, the unit of memory that programmers can access is an array of bytes; in Java, the unit of memory that programmers can access is an abstract object. Because registers can also access a byte-array memory unit, this means that C programmers can directly access the underlying layer and perform more operations. This is also one of the important reasons why C programmers look down on Java programmers. However, more access does not only mean more freedom; it also means more responsibility, because without object-level abstraction, large C programs in particular may unexpectedly throw buffer overflows, array out-of-bounds errors, garbled text, and other problems that are difficult to trace back to their root cause.

#### 1.2 Memory Allocation and Reclamation

For C, programmers need to actively request and release memory. For Java, because the VM exists, the GC automatically reclaims unreachable objects. At the same time, when the GC thread reclaims garbage, it causes STW (Stop the World), which slows down program performance. In addition, because object cleanup is handled by the VM, the time at which an object is cleaned up is actually unpredictable. By comparison, C programmers can fully control the timing of memory allocation and reclamation and can completely know the state of memory, which Java programmers cannot do. However, if a C program forgets to `free` memory, it can also cause incalculable damage.

From the perspective of memory handling, C programs have unquestionable control over memory, while Java programs hand memory operations over to the VM after introducing an abstraction layer, turning them into indirect access. At the same time, because of the VM, Java programmers can write code freely without worrying about major bugs, which makes Java very easy to learn and also leads to uneven skill levels among Java programmers, a fact that has long been criticized in the industry.

### 2. Memory Structure in Java

The memory structure of Java is almost always a must-ask interview question, so let us review it again here.

> The following memory structure is based on JDK 8

#### 2.1 Basic Concepts

* **Virtual machine stack**: private to each thread; each non-native method corresponds to one stack frame. A stack frame includes the local variable table (the basic unit is a slot, which stores method parameters and internal variables), the operand stack (which stores calculation parameters and results), dynamic linking, and so on
* **Native method stack**: private to each thread; responsible for native methods
* **Program counter**: private to each thread; records the bytecode execution position of a thread
* **Heap**: shared by all threads; used to store instances. It is the largest area in the JVM and the main area managed by GC. In JDK 7 and earlier, it is divided into the young generation *(Eden 8, From Survivor 1, To Survivor 1)* and the old generation. The ratio of the young generation to the old generation is 1:2
* **Method area**: stores class structure information. Except for the runtime constant pool, everything else is stored in MetaSpace
  1. Runtime constant pool: at runtime, the data in the constant pool is placed here, including the string constant pool. This actually resides in the heap and can change dynamically, such as with `String#intern()`
  2. Constant pool: stores compile-time generated literals (text strings, the values of the eight basic types, and constants declared as `final`) as well as symbolic references (the fully qualified names of classes and methods, field names and descriptors, and method names and descriptors). Its size is known before runtime. It is organized by class
  3. Method bytecode: stores the bytecode of each method, which is interpreted and executed by the JVM by relying on the operand stack and local variable table

For theoretical background, see [Bleem1 (in Chinese)](https://mritd.com/2006/01/02/java-memory-overview-of-vm-memory-auto-management-and-memory-regions/), [Bleem2 (in Chinese)](https://mritd.com/2006/01/02/java-memory-method-area-and-runtime-constant-pool/)

#### 2.2 Program Demonstration

For a class, it mainly consists of two parts: attributes and methods. These two parts correspond one-to-one with data structures and algorithms in our computer science fundamentals. For a C program, data structures are stored in the heap and algorithms are stored in the code segment. Below, we use a program to show where these two parts of a Java program are stored.

> The allocation scenario does not consider TLAB, JIT, escape analysis, and so on. It also does not consider regions such as Eden and Survivor

```java
class MemoryStructTest {
    private static final String HELLO_WORLD = "hello world!";
    public static void main(String... args) {
        String helloWorld = HELLO_WORLD;
        System.out.print(helloWorld);
    }
}
```

When this program is compiled, class-loaded, initialized, and run, what does it look like in memory?

* After class loading, the information for the `MemoryStructTest` class is stored in the method area. This includes fields, methods, the constant pool, static variables, the class name, and so on
* The final initialization step of class loading initializes the static variable `HELLO_WORLD`. At this point, the `String` class is also class-loaded. The `String` class is loaded into the method area in the same way described above, and the reference to the `HELLO_WORLD` string is placed in the string constant pool, while the actual string is stored in the heap. The local variable `helloworld` is stored in the virtual machine stack
* After the program starts running, some content from the constant pool is copied into the runtime constant pool, and then the VM begins interpreting and executing the bytecode of the `main` method line by line in the method area
* When execution reaches line 5, the `System.out` class is class-loaded into the method area, and then the static method in the method area is invoked to print the local variable `helloWorld`

The following diagram can be obtained:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/520f416a_java-memory-1.png)

One thing to note is that for `String` and the basic types, if they are not explicitly created with `new`, they reside in the constant pool. If they are created with `new`, they are created in the heap.

### 3. Storage Formats of Specific Types

#### 3.1 Storage Format of a Parent Class

This is a memory diagram I drew in my sophomore year of college. Looking at it now, it still has some value, so I am sharing it again:

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

![Memory layout diagram](https://img-blog.csdnimg.cn/20190815120936937.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NvZGVyX3doYXQ=,size_16,color_FFFFFF,t_70)

#### 3.2 Storage Format of an Interface

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

![Object memory layout diagram](https://img-blog.csdnimg.cn/20190411183056417.PNG?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NvZGVyX3doYXQ=,size_16,color_FFFFFF,t_70)

> PS: The "heap · class" label above should be changed to "method area".

#### 3.3 Storage Format of an Inner Class

An inner class is parsed through syntactic sugar into an ordinary class, and then it is the same as above.

#### 3.4 Storage Format of an Array

In Java, an array is also an object. This abstraction greatly improves the safety of array operations and avoids the array out-of-bounds memory overwrite problems seen in C programs.

A program containing arrays, interfaces, classes, and inheritance:

> **Note: This program is entirely a demo for illustrating the memory logic model of interfaces, classes, and so on**  
> **Also: this program is somewhat redundant, but it can indeed illustrate inheritance relationships. The memory logic model was drawn by hand, and only some important parts were drawn, not as detailed as the previous program**

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

#### 3.5 Storage Format of Basic Data Types

For basic data types, if they are local variables, they are directly allocated on the stack according to the byte specification. If they are global variables of a class, they are allocated in the heap along with the initialization of the instance.

If a certain attribute of a class instance is another instance, then there is a pointer to that other instance. If the attribute is a basic type, then there is no pointer; the space of that many bytes is allocated directly.

> Basic type sizes: `byte` 1 byte, `char` 2 bytes, `short` 2 bytes, `int` 4 bytes, `float` 4 bytes, `long` 8 bytes, `double` 8 bytes, `boolean` unspecified


### 4. Afterword

Actually, I already knew all of these things at this time last year, but I did not yet have a coherent overall picture. After summarizing them today, I finally had a feeling of sudden clarity.

But the more I understand, the more I realize how much I still do not know. Keep going.


> No matter how elegant the data model provided by a high-level language is, after it is compiled into machine code, it is simply a large array addressed by byte (8 bits). And when a machine accesses memory, it does so through addresses.
>
> What is the difference between a 32-bit machine and a 64-bit machine? It refers to the address bus. A 32-bit machine means the program's address can occupy 4 bytes, and the accessible address space is 4 GB. A 64-bit machine means the program's address can occupy 8 bytes, and the accessible address space is 2^64 bytes

