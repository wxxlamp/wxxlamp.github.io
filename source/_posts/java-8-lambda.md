---
title: "Java8的函数式编程"
tags:
   - Java
   - Lambda
date: 2021-08-22 9:52
categories:
   - 基础夯实
description: "本文系统介绍Java 8函数式编程与Lambda表达式的核心知识，从Lambda的数学起源讲起，详细解析Function、Consumer、Supplier三大基础函数式接口的用法及其在JDK中的应用，并展示如何自定义函数式接口。同时结合责任链模式、观察者模式、策略模式等常见设计模式，演示Lambda如何大幅简化代码，帮助读者将Lambda从被动调用提升为主动设计。"
---

Java8发布了一系列高效的操作方式，其中lambda就是一个很重要的特性。譬如我们可以利用lambda代替匿名内部类，可以更方便的创建线程，更方便的使用接口。同时Java8还结合lambda定义了一系列常用且高效的api，如forEach，Stream，Optional等等。

### Lambda的起源

Lambda起源于20世纪40年代，是一种数学表达式λ，也是一种函数演算。这在和面向对象，面向过程并称三大编程方式的函数式编程中用的极为广泛。

其实不止Java，C++也早已引入了Lambda编程，同时学习Lambda我们要知道λ的始祖是Lisp语言，它的出现要早于C和Java。

我们可以称lambda为函数式编程，什么是函数式编程呢？这个要从[λ演算](https://cgnail.github.io/academic/lambda-1/)说起。lambda演算要求一切皆函数，参数是函数，返回值也是函数。有这个特点之后，就会给我们编程带来很大的便捷性。假如说我们方法的参数可以是函数，那么我们就可以把只有一个方法的接口作为参数传递到函数中，再进一步来说，我们就可以通过lambda演算来代替匿名内部类，这也是lambda演算在Java中最重要的一个应用。

### Lambda的使用

对于Java8来说，它提供了三个基础的函数式接口，分别是`Consumer`，`Supplier`，`Function`，这三个接口场景不同，分别对应着消费，生产和函数，这三个接口在Java的java.util.function包中

#### 1. Function

这个是最经典的函数式接口，它的作用就表现出了函数根本的作用：**输入入参，返回出参**，即：`R apply(T t)`。最常见的使用方式如下：

```Java
// 因为只有一个入参，所以第一个括号中需要写一个参数，且类型为T
// 因为只有一个出参，所以函数体的doSomething需要返回R类型
Function<T, R> func = (t) -> doSomething();
public R doSomething();
```

我们知道juf包中也有一个比较重要的函数式接口：`Predicate`，它的作用是输入入参，返回布尔值，即：`boolean test(T t)`。乍一看是一个新接口，其实它只不过是`Function`的特殊形式，下面的两个代码块作用是一样的：

```Java
Predicate<String> predicate = (t) -> "test".equals(t);
System.out.println(predicate.test("111"));

Function<String, Boolean> func = (t) -> "test".equals(t);
System.out.println(func.apply("111"));
```

在JDK自带的包中，也有很多使用到`Function`接口的方法，如我们在使用`Stream`时经常希望拿到list中对象的某一字段，就会使用`Stream#map(Function mapper)`，它通过map这个接口，将我们的参数进行了转化。

除了`Predicate`之外，juf还对`Function`做了其他的延伸，如`BiFunction`，`ToDoubleFunction`，`ToDoubleBiFunction`等等，大家可以自行下去了解一下

#### 2. Consumer

`Consumer`对应着消费者，从字面意思来理解它的功能，应该是只有入参，没有出参的函数式接口：`void accept(T t)`。最常见的使用方式如下：

```Java
// 因为只有一个入参，所以第一个括号中需要写一个参数，且类型为T
// 因为没有出参，所以函数体不能有返回值
Consumer<String> consumer = (t) -> System.out.println(t);
consumer.accept(test);
```

`Consumer`也在JDK自带的很多包中使用，如我们常用的`Iterable#forEach(Consumer action)`，它的作用就是传入集合中的元素，然后进行处理，不进行输出。除此之外，`Optional#ifPresent(Consumer consumer)`也很好的解决了NPE的问题

同`Function`一样，juf也对`Consumer`做了相当多的扩展，如`BiConsumer`, `DoubleConsumer` 等等

#### 3. Supplier

`Supplier`跟`Consumer`是一对，`Supplier`对应着生产者，它跟`Consumer`恰好相反，没有函数入参，只有函数出参：`R get()`。最常见的使用方式如下：

```Java
// 因为没有入参，所以第一个括号中不应该有参数
// 因为只有一个出参，所以返回值的类型应该为R
Supplier<String> supplier = () -> “test”;
System.out.println(supplier.get());
```

相信大家在代码开发的过程中都非常恶心NPE，所以JDK提供了`Optional`。`Optional`会通过`Supplier`来对NPE的异常进行重新抛出： `Optional#orElseThrow(Supplier exception)`，或者是通过`Optional#orElseGet(Supplier other)`去获得另一个非空的参数，这几个还是很不戳的

#### 4. Custome

了解了上面的三种基础函数式接口后，我们甚至也可以自定义一些我们需要的函数式接口，如`Comparator#compare(T o1, T o2)`，下面可以试着自定义一个

```Java
@FunctionalInterface
interface Test<A,B,C> {
  A test(B b, C c, int d);
}
Test<String, StringBuffer, Boolean> test = (b, c, d) -> b.append(d).append(d).append(c).toString();
System.out.println(test.test(new StringBuffer("111"), true, 1));
```

### Lambda与设计模式

我们在日常开发工作中，常见的设计模式如策略模式，单例模式，工厂模式，模板方法模式，建造者模式，代理模式，观察者模式，责任链模式等等，我们如果把Lambda看成函数级别的接口的话，会大大简化程序的代码量的（其实也就是通过简化类的创建来简化代码量）

#### 1. 责任链模式

```Java
class ChainHandler {
    Function<String, String> first = (s) -> s + " fisrt process ";
    Function<String, String> second = (s) -> s + "second process ";
    Function<String, String> third = String::toUpperCase;

    public String runHandler(String input) {
      	return first.andThen(second).andThen(third).apply(input);
    }
}
```

#### 2. 观察者模式

```Java
class Observer {
    Consumer<String> alibaba = (msg) -> System.out.println("alibaba get the " + msg);
    Consumer<String> tencent = (msg) -> System.out.println("tencent get the " + msg);
    Consumer<String> baidu = (msg) -> System.out.println("baidu get the " + msg);

    // 注册监听者
    List<Consumer<String>> observers = ImmutableList.of(alibaba, tencent, baidu);

    public void notify(String msg) {
      	observers.forEach(e -> e.accept(msg));
    }
}
```

#### 3. 策略模式

```Java
public String getSuitableEle(List<String> list, Predicate<String> strategy) {
    for (String s : list) {
        if (strategy.test(s)) {
          	return s;
        }
    }
    return null;
}
Predicate<String> hasJj = (s) -> s.contains("jj");
Predicate<String> notEmpty = (s) -> !s.isEmpty();
Predicate<String> end = (s) -> s.endsWith("666");
List<String> list = ImmutableList.of("12345","6666", "jj is big");
getSuitableEle(list, notEmpty);
getSuitableEle(list, notEmpty.and(hasJj));
getSuitableEle(list, notEmpty.and(hasJj).and(end));
```

### 后记

Java中的lambda我自己之前用的时候仅限于调用Stream，Optional，forEach等JDK原生的接口，从来没有自己设计过对应的lambda，这次总结一下，也算是填补了之前的一个大空白