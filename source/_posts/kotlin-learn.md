---
title: "Kotlin学习笔记"
date: 2020-12-24 18:26
tags:
   - Kotlin
categories:
   - 基础夯实
description: "Kotlin语言入门学习笔记，对比Java语法差异，涵盖空安全、扩展函数、数据类等特性。"
---

作为一门Jvm的衍生语言，Kotlin在安卓阵营大放异彩，Google官方在19年IO大会上宣布全局支持Kotlin，究竟是人性的扭曲还是道德的沦丧？昨天组内安卓大神分享了Kotlin，今天我又参考了Google官方的文档，特来整理一下。

### 壹. Kotlin的历史发展

Kotlin是一种在Java虚拟机上运行的静态类型编程语言，它主要是由JetBrains开发团队所发展出来的编程语言，其名称来自于圣彼得堡附近的科特林岛。

* 2010年，JetBrains着手开发Kotlin项目。
* 2011年7月，JetBrains发布Kotlin项目。
* 2012年2月，JetBrains在Apache 2许可证下开源Kotlin项目源码。
* 2016年2月，JetBrains发布第一个稳定版本Kotlin 1.0，并许诺保持向后兼容。
* 2017年3月，Kotlin 1.1版本发布，正式支持JavaScript，并新增了诸多新功能和特性。
* 2017年5月，Google I/O大会上，Google官方确定支持Kotlin语言。
* 2019年，Kotlin称为Android移动开发首选。

### 贰. Kotlin的独到之处

总的来说，相对于Java来讲，Kotlin有以下三个特点：

1. 简洁：您可以使用更少的代码实现更多的功能。表达自己的想法，少编写样板代码。
2. 更安全的代码：Kotlin 有许多语言功能，可帮助您避免 null 指针异常等常见编程错误。包含 Kotlin 代码的 Android 应用发生崩溃的可能性降低了 20%。

3. 可互操作：您可以在 Kotlin 代码中调用 Java 代码，或者在 Java 代码中调用 Kotlin 代码

### 叁. Kotlin的语法特性

现在，我们就上面的三个特点，来分析下Kotlin的语法：

#### 1. 简洁

* **类的简化**

  Kotlin允许一个方法体没有类，当kotlinc将代码编译为字节码的时候会自己加上

  ```java
  fun main() {
      println("test")
  }
  ```

  对应的Java代码如下：

  ```java
  class Demo {
      public static void main(String[] args) {
          System.out.println("test");
      }
  }
  ```

* **Bean对象的简化**

  1. 简化setter和getter方法

     ```kotlin
     // kotlin默认带有setter和getter的，除非我们标明private，否则就可以直接访问，同时它的属性变量默认是private，如果我们显示声明private，则不会生成getter和setter方法
     public class MyKotlinClass {
        val a: Int = 1
        var b: Int = 1
        val c = 1
        var d = 1
            private set
     }
     fun example() {
        val myClass = MyKotlinClass()
        myClass.b = 2
     }
     ```

  2. 简化成员声明

     ```kotlin
     class Hero(val power: Int) {  // 表明已经声明了一个成员 private final Integer power;
        fun vs(opponent: Hero): Hero {
            return if (power > opponent.power) {
                this
            } else {
                opponent
            }
        }
     }
     ```

  3. 简化hashCode、equals，toString等Object实现方法

     ```kotlin
     /*编译器自动从主构造函数中声明的所有属性导出以下成员：
     equals()/hashCode()
     toString() 格式是 "User(name=John, age=42)"；
     componentN() 函数 按声明顺序对应于所有属性
     */
     data class User(val name: String, val email: String)
     ```

* **fianl属性的简化**

  ```kotlin
  public class MyKotlinClass {
     val a: Int = 1 // final
     var b: Int = 1 // 非final
  }
  ```

* **for循环的简化**

  Kotlin的for循环类似于Python

  ```kotlin
  fun test() {
      val item2 = listOf("apple", "banana", "kiwifruit")
      for (item in item2) {
          println(item)
      }
  
      //或者
      val items = listOf("apple", "banana", "kiwifruit")
      for (index in items.indices) {
          println("item at $index is ${items[index]}")
      }
  }
  ```

* **lambda的简化**

  1. Kotlin允许将函数赋值给参数

     ```kotlin
     val f1 = { a: Int, b: Int -> a + b }
     ```

  2. Kotlin允许将函数传参给方法，而不是使用接口

     ```kotlin
     val a = 1
     val b = 2
     
     val f1 = { a: Int, b: Int -> a + b }
     
     fun f2(a: Int, b: Int): Int {
        return a + b
     }
     
     fun f3(a: Int, b: Int, fn: (Int, Int) -> Int): Int =
            if (a > b) fn(a, b) else a - b
     
     class MyKotlinClass {
        fun test() {
            print(f1(a, b))         // => 3
            print(f2(a, b))         // => 3
            print(f3(a, b, f1))     // => -1
            print(f3(2, 1, ::f2))   // => 3
        }
     }
     ```

* **字符串的简化**

  Kotlin中拼接字符串不会使用+号，而是通过$string的方式，这类似于我们打日志时的格式。不过如果换行的时候，IDE还是会自动加上一个+号，我们可以把这个语法特性理解为语法糖

  ```kotlin
  class MyKotlinClass {
     val name = "Omar"
     val surname = "Miatello"
     val example = "My name is $name $surname"
  }
  ```

* **返回值的简化**

  1. Kotlin允许当返回值为空时可以不写返回值
  2. 在Kotlin中，空返回值被记为Unit

* **方法的简化**

  1. Kotlin允许没有方法体的存在

     ```kotlin
     fun f(a: Int, b: Int): Int = a + b
     fun test() {
         print(f(1, 2))
     }
     ```

  2. Kotlin允许方法体自己初始化参数

     ```kotlin
     fun sum2(a: Int = 1, b: Int = 3): Int? {
         return a + b
     }
     fun sum3(a: Int = 1, b: Int): Int? {
         sum2(a = 3)
         sum2(b = 4)
         return a + b
     }
     ```

* **语言类型的增强**

  1. 编译器的类型推断

     ```kotlin	
     public class MyKotlinClass {
        val a: Int = 1 // 显式声明类型是Int型
        var d = 1 // 自动推断出类型是Int型
     }
     ```

  2. 没有基本类型，只有包装类型。在Kotlin中，我们不能把类型定义成int、byte、long等，只能是Int，Byte，Long等。不过，Kotlin在编译为字节码的时候，还是会把简单的方法编译为基本类型

* **类方法的增强**

  Kotlin可以在其他任何一个地方为任何一个类增加方法，如：

  ```java
  fun String.isBig(): Boolean {
     return length() > 10
  }
  fun example() {
     "why?!".isBig()                 // false!
     "P90, RUSH B, ...".isBig()   // true!
  }
  ```

  这等价于：

  ```java
  class MyUtils {
     static boolean isBig(String str) {
         return str.length() > 10;
     }
  }
  class MyJavaClass {
     void example() {
         MyUtils.isBig("why?!");
         MyUtils.isBig("P90, RUSH B, ...");
     }
  }
  ```

  不过，在为类增强方法的同时，我们需要把这些增强的方法集中起来管理，不然后果也挺可怕的

  基于这样的增强，Kotlin延伸出了几个操作符，常见的有let和apply

  ```kotlin
  customer?.let {
      doSth(it.id)
  }
  
  if (customer != null) {
      doSth(customer.id)
  }
  
  public inline fun <T, R> T.let(block: (T) -> R): R = block(this)
  
  ```

  ```kotlin
  val list = listOf(StringId(1, "今天"), StringId(2, "最近7天"), StringId(3, "近30天"))
  
  holder.time.setItems(list)
  
  holder.time.setSelectedItem(list[1])
  
  holder.time.setOnSingleSelectListener {
     time = it.id
     holder.time.setTitle(it.title)
  }
  
  holder.time.apply {
     setItems(list)
     setSelectedItem(list[1])
     setOnSingleSelectListener {
         time = it.id
         setTitle(it.title)
     }
  }
  
  public inline fun <T> T.apply(block: T.() -> Unit): T { block(); return this }
  
  ```

* **switch的增强**

  其实在Kotlin中没有switch，不过有比Switch更强大的when

  ```kotlin
  fun describe(obj: Any): String =
      when (obj) {
          1 -> "One"
          "Hello" -> "Greeting"
          is Long -> "Long"
          !is String -> "Not a string"
          else -> "Unknown"
      }
  ```

* **懒加载的增强**

  在Kotlin中，一行代码就可以写出懒加载的线程安全的单例模式

  ```kotlin
  class MyKotlinClass {
     val item by lazy { MyItem() }
  }
  ```

#### 2. 安全

Kotlin的安全主要指的是它可以在编译期确定空指针，如果返回值或者属性表明不能为空，那么NPE就会在编译期被检测出来。

```kotlin
// 对于类型来说，如果不加?，则说明该值一定不为空，Kotlin会在编译期禁止null值出现，只有出现?标志符时，才允许可以为空
class MyKotlinClass {
   var a: String = "ciao"
   var b: String = null  // Error at compile time，因为声明改成参数不能为空
   var c: String? = null
   var d: String? = "ok"

   fun example(e: String, f: String?) {
       e.length()
       f.length()        // Error at compile time，Kotlin不允许调用可能为空值的方法
       f?.length()

       if (f != null) {
           f.length()
       }
   }
}
```

不过，因为Kotlin可以和Java互相调用，假如说Kotlin调用了Java的一个接口实现，Java的返回值可能为空，Kotlin声明该值不能为空，那么就还可能出现运行时异常

同时，当？操作符用到表达式中，它还可以判断该表达式是否为空：

```Kotlin
func test(var a: String?) {
	val foxSay = a ?: "No one knows" // 等价于String foxSay = s != null ? s : "No one knows";
}
```

#### 3. 互操作

除了上面的语法特性外，还有其他的，如异常的抛出、is代替instanceof，Java的三目运算符与Kotlin的条件表达式，类默认final等等这些语法表达上的不一样。但是除了这些，kotlin的其他几乎和Java中一样，我们可以通过IDE将Kotlin转换为Java代码来比较。

同时，因为Kotlin和Java都是在Jvm上运行的，Kotlin也具有了`Write Once, Run Anywhere`的牛逼特性。

有句老话说的好，如果解决不了问题，就加一层中间件。Jvm不正是这样一层中间件吗？同时，它也是一种抽象，而它的扩展，正是Jvm系列的种种语言。

### 肆. 后记
个人认为，程序员必须了解几种语言，这几种语言必须包含以下特点：
1. 解释型语言（Java），编译型语言（C/C++）；
2. 动态语言（JavaScript），静态语言（Java，C/C++）；
3. 面向过程语言（C），面向对象语言（Java/C++/Golang），面向函数语言（Lisp）；