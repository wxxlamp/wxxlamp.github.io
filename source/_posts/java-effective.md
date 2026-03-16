---
title: "Java编程技巧"
tags:
   - Java
categories:
   - 基础夯实
date: 2022-03-22 10:36
description: "本文结合《Effective Java》与实际工作经验，总结了Java编程效率提升的实用技巧。内容涵盖静态工厂方法与建造者模式的使用场景、防止重复创建对象的策略、单例模式的安全写法，以及对象比较、方法签名设计哲学、泛型正确使用姿势（通配符、泛型方法、列表优于数组）、Stream与Lambda的无副作用使用规范、受检异常的谨慎抛出，以及并发中线程安全和线程通信的处理思路。"
---

我把业务代码的开发分为效率和性能两个部分，对于效率来说，又可以分为开发提效和架构提效。本章是结合《Effective Java》加上我平时的工作经验得出的一些Java编程技巧，用于开发提效。

## 对象的创建和销毁

### 1. 静态工厂方法
静态工厂方法可以方便的构造一个简单实例，使得代码更易读，不用每次都创建对象。
```java
public static Boolean valueOf(boolean b) {
	return b ? Boolean.TRUE : Boolean.FALSE;
}
```
在业务应用中，可以应用在简单的Response中，尤其是不变的success响应，如下面所示，这样在业务逻辑返回success时，只需要调用`AddActivityPointsResponse.ofSuccess()`即可，不仅更清晰，而且不用频繁创建成功的响应对象

```java
private static AddActivityPointsResponse SUCCESS = AddActivityPointsResponse.of(true, CommonResponseCode.SUCCESS.name());
public static AddActivityPointsResponse ofSuccess() {
    return SUCCESS;
}
```
### 2. 建造者方法

创建一个有多个参数的对象，常见的有两种方法，一种是通过构造器传参进行new，另一种是先创建一个空参数对象，再通过JavaBean模式的setter方法去附值。

但是，这两种方法都有些问题，当参数过多的时候，第一种方法在客户端的可读性会大大降低；而如果用setter方法去为对象增加参数的话，则无法保证实例自身的一致性。

不过，还有第三种不常见的方法，可以通过建造者模式来保证可读性和一致性。不过可惜的是，建造者模式会增加稍微的内存的消耗，这三种方法没有对错，都是不同的抉择。

鉴于建造者模式代码也比较冗余，可以在应用内使用`Lombok`，但是`Lombok`尽量不要在api中使用，因为应用无法保证，也无法要求客户端兼容`Lombok`这种鬼东西

### 3. 防止创建重复对象

虽然对象可以被JVM自动GC，但是频繁的创建和销毁相同的对象，还是会造成计算资源和内存的浪费。解决这种问题一般有两种办法，一个是从客户端约束，一个是从服务端约束。

如果从客户端约束，则需要开发者注意两点：

1. 如果一个类被使用很多次，则需要创建一个容器集中管理，避免频繁new。Spring的SingletonBean即是这种思想
2. 借助Jvm的常量池来防止对象频繁创建对象，如使用`String a = "a"`而不是`String a = new String("a")`；使用`Boolean.TRUE`而不是`new Boolean(true)`；`Integer i = -128 ~ 127`，除了Integer还有Byte,Short,Integer,Long,Character
3. 尽量避免自动装拆箱，如使用`int i = 1000`而不是`Integer i = 1000`
4. 通过池化技术来减少对象创建，如连接池，线程池。但是要注意共享对象的数据安全和通信问题

如果从服务端约束，则需要使用单例模式来显示使用者，单例模式经常看到，不仅用的多，而且面试也会经常问到。

单例模式分为懒汉式和饿汉式。饿汉式的写法非常简单：`private static final Instance INSTANCE = new Instance();` 即可保证单例。

但是因为饿汉式是系统在启动时创建对象，会造成启动速度缓慢，在对象真正被使用之前会造成内存浪费等，所以在面对一些大对象如`Connection`的时候，需要使用懒汉式的单例模式，对于懒汉式的单例模式，有以下问题需要避免：

1. 并发问题：使用双重锁模式或者静态内部类解决
2. 反序列化问题：禁用`readObejct()`
3. 类加载器问题：对单例类只使用一个类加载器      

并发问题和反序列化问题，均可以通过`enum`来解决。在实际的工作过程中，可能是因为懒汉式的单例比较难写，更能体现开发者的编程技巧，导致代码里几乎都是懒汉式的单例，但是我认为，如果不是涉及到很大的启动开销和资源浪费，使用饿汉式单例显然是一种更明智的选择

### 4. 避免实例化对象

一般我们在写工具类或者常量类的时候，直接使用其静态方法即可，不用实例，方法如下：

1. 禁止构造：设置构造方法为私有
2. 禁止反序列化：`readObject()`抛出异常
3. 禁止反射：构造方法只能调用一次

但是，说实话，一般使用方法1就可以告诉使用者该方法不可实例化了，方法2和3基本不怎么用 -_-

## 对象的比较 

### 1. 比较的区别

1. 对于==来说，用来判断对象的地址是否相等，即会去判断是否是同一个对象，换句话说，是判断对象是否“物理相等”。也可以用来判断基本类型的值是否相同
2. 对于equals来说，是使用者自己来实现的。不过按照不成文的规定，equals是为了判断两个对象的值是否相等
3. 对于hashCode来说，也是使用者自己来实现的，主要是为了计算对象实例的散列值，用于诸如`HashMap`,`HashSet`等一些列基于散列的集合。所以，在散列容器中存在且起作用的值都必须重写hashCode。同时， 因为散列容器在比较的时候，会先比较hash，再通过equals比较，所以，规范要求，如果equals相等，hashCode值必须相同，反之，则不一定
4. 对于compareTo来说，需要实现`Comparable`接口，主要是用于数值类的比较。同时，又因为比较工具类也与该方法相关，所以所有与排序相关的对象都应该实现该方法。同时要注意，比较不建议直接运算，而是使用基本类型的比较方法，如：`Interger.compare(int ,int)`

### 2. 常用的比较方式

1. String实例对象用equals方法比较，同时需要顺序而产生的NPE问题
2. 因为枚举是天然的单例，所以枚举用equals和==都可以用来比较
3. 数值的包装类用compareTo来比较
4. 基本类型直接用==比较即可
5. 排序类的对象也需要用compareTo来比较

## 方法规约

### 1. 不要让客户端额外判断

1. 集合要返回零长度，如`Collections.emptyList()`，而不能直接返回null。这样会让调用方多加一次判断，更加麻烦
2. 谨慎返回`Optional`，返回`Optional`和抛出受查异常一样，都会强制让调用方额外关心该方法的特殊返回值，不同的是，抛出异常会有一定的开销，而`Optional`则没有这种可能
3. 在微服务系统中，调用方往往只关心provider的方法是否可以重试，而不会去关心提供方的具体异常。所以应用不要轻易抛出异常细节，最好通过code和msg告诉客户端是否应该重试，以及如果不能重试，请在code和msg中说明原因（如参数校验失败），便于问题排查

### 2. 注意兜底校验

其实不止是在方法中，在正常的业务中也是一样的。举个例子，在微服务应用中，不要因为上游做了校验自己就省事不做校验，除非性能要求特别特别高，否则一定要在链路的每个节点中都加入诸如`NotNull` `NotBlank`等的校验

### 3. 方法签名的设计哲学

1. 设计阅读性高的方法签名
2. 为方法增加注释。我在实践过程中，发现即使IDEA抛出WARNING的警告，大家也总是不太愿意为方法添加注释。一半来说，在注释中说明方法的用途是很必要的，虽然刚开始代码可能还简单，但是系统都会经过多次迭代，谁能保证方法的逻辑一定不会改变呢？
3. 在使用可变参数的时候，最佳的方式是`void test(int arg1, int... args)`这种方式可以避免运行时的NPE
4. 设计重载方法的时候注意入参的类型，如果每个重载方法的入参是继承关系的话，那么将会导致意想不到的结果，如`void test(Collection<?> c)`和`void test(List<?> list>`。因为重载调用的判定是在编译期决定的，所以很有可能即使如参为list，调用的也是第一个方法。
5. 如果有多种入参的情况下，可以借鉴一下`Collectors.toMap()`方法的调用链

## 泛型的使用

泛型的作用就是在类型或者方法在实例化的时候，确定该类或者方法所使用的具体类型，增加程序的扩展性。

在泛型出之前，通过Object实现的类型转换需要在运行时检查，如果类型转换出错，程序直接GG，可能会带来毁灭性打击。而泛型的作用就是在编译时做类型检查，这无疑增加程序的安全性。

### 1. 不要使用原生类型

泛型能够有效的帮助开发者对容器的类型进行限制，能让错误尽可能在编译期提前发现，这是`Object`或者原生类型所做不到的。下面举一个原生类型的问题：

```java
List list = new ArrayList(10);
list.add("111");
list.add(111);
for(Object ele: list) {
    System.out.print((int)ele); // error
}
```

在平时工作中，因为有的业务开始的比较早，导致部分老代码都是原生类型的，虽然都是`@suppressWarnings("unchecked")`，但是还是有点影响可读性，建议及早改掉。
但是有些时候，也必须使用原生类型，如：

1. 获取`class`，如`List.class`
2. 使用`instance of`

### 2. 无限通配符的用法

无限制通配符相对来说有点奇怪，因为它表示一种未知类型，如果用无限制通配符容器作为参数，会导致该容器只能被赋值为null，显得莫名其妙。但是它在特殊情况下还是有点用的：

1. 泛型强转：当使用`instance of`之后，就需要用无限制通配符来强转类型
2. 作为返回值：如`Class<?>`
3. 作为工厂类容器的键值：在很多业务代码中，我们一般会通过Map进行路由，当Map中的K或者V是泛型类的时候，我们就可以使用无限制通配符的方式来实现，如下：

```java
public class StrategyFactory {

    // Map的value为泛型类
    private static final Map<String, StrategyService<?>> SERVICE_MAP = new ConcurrentHashMap<>(16);

    @SuppressWarnings("unchecked")
    public static <T> StrategyService<T> get(String key) {
        return (StrategyService<T>)SERVICE_MAP.get(key);
    }

    public static <T> void put(String key, StrategyService<T> value) {
        SERVICE_MAP.put(key, value);
    }
}
```

### 3. 使用泛型方法

当泛型在类中使用的时候，会对泛型类的实例化进行限制。同时，对于静态方法，也可以使用泛型方法对方法的入参和出参进行限制
譬如，我们可以使用泛型方法来要求该方法的出入参一致：

```java
public static <E> Set<E> union(Set<E> s1, Set<E> s2);
```

### 4. 使用列表而不是数组

因为数组具有协变性，所以当出现数组元素类型错误的时候，并不能在编译时发现，而是等到运行失败才抛出异常。

所谓协变，可以简单理解为因为`Object`是`String`的父类，所以`Object[]`同样是`String[]`的父类。这咋一听没毛病，但是下面的代码就会因为协变而出问题：

```java
Object[] objArr = new String[1];
objArr[0] = 111; // 运行时异常而不是编译时异常
```

同时，因为泛型具变而数组协变，所以也不要将他们混在一起使用。这或许浪费了点性能，但是对于大部分业务代码来说，可读性比性能重要得多。

### 5. 用有限通配符提高API灵活性

就像上面所说，因为泛型具有具变性，导致`List<Object>`和`List<String>`看起来是相同的容器，但是在编译期却没有半毛钱关系，所以下面这种泛型写法是错误的：

```java
List<Object> objList = new ArrayList<String>(); // 编译时异常
```

但是，有很多时候我们希望泛型中是有继承关系的，如`void push(Iterable<E> src);`我们希望src不仅可以接受E类型的，还可以接受E的子类，这种情况就需要使用`void push(Iterable<? extends E> src);`同时，如果我们希望其接收E的父类，就可以使用`void pop(Iterable<? super E> src);`来完成。

有一个规则叫PESC，即如果泛型类作为提供者，就是用extends，反之，则使用super

## 流和Lambda

Stream和Lambda是在Java8中出现的新概念。Lambda的基本操作我在之前的[博客](https://wxxlamp.cn/2021/08/22/java-8-lambda/)中讲过，而Stream则主要用于结合Lambda对集合的操作，更高效，更安全，性能更好。

### 1. 流的常用操作

下面列举一下常见的操作

#### 1. 中间操作

1. 映射：通过`map(Function)`来将流中的元素映射成其他类型；通过`flatMap(Function)`将流中的每个元素都转换为Stream
2. 过滤：通过`fliter(Predicate)`来将流中不符合条件的元素进行过滤
3. 排序：通过`sorted(Comparator)`对实现流中元素的排序

#### 2. 终止操作

1. 遍历：通过`foreach(Cunsumer)`对集合中的元素进行遍历
2. 最值：通过`min(Comparator)`/`max(Comparator)`获取整个流中的最值
3. 集合：通过`collect(Collector)`将流转化为集合，Collector中除了toMap,toSet,toList之外，还有主要用于map`grouping`和`joining`等牛逼操作值的一看
4. 计数：通过`count()`对流中的元素进行计数
5. 规约：所谓的规约，就是对集合中的元素进行操作，同时返回操作后的值。可以通过`reduce(T, BiFunction)`来完成。其实所谓的最值，集合和计数，底层都是通过规约实现的

### 2. 优先选择无副作用函数

Stream提供了功能强大的api用于在流中处理数据，用专业的api处理特殊的需求

1. foreach应该只用于报告流的结果，而不应该计算。特别注意，我们如果只是把stream当作一种简单的遍历，那么stream对于我们来说则毫无用处。从我的开发经历中看，很多代码都像下面这样：

```java
// 修改前
streamList.forEach(e -> {
    if (contains(e)) {
        LOGGER.error("error" + e);
    }
});
// 修改后
listStream().filter(this::contains)
    .forEach(e -> logger.error("error" + e));
```

2. 很多时候，我们会把在stream的foreach中进行遍历，遍历过程中，会把流中的元素放到其他代码已经初始化完成的集合中，这也是不符合规范的做法，我们应该学会利用`Collectors`中的`toMap``groupingBy`和`joining`方法： 

```java
Map<String, String> HADLER_CACHE = Maps.newHashMap();
// 修改前
listStream().forEach(e -> {
    HANDLER_CACHE.put(getKey(e),e.getHandler);
});
// 修改后
HANDLER_CACHE.putAll(listStream()
    .collect(Collectors.toMap(k -> getkey(k), v -> v.getHandler)));
```

### 3. 避免基本类型的装箱

不管从内存占用还是计算效率来讲，如果流或者集合中的元素类型为基本类型，则要用专门的方法对其进行处理。如Stream中的`mapToInt`/`mapToLong`和`flatMapToInt`等，以及函数式接口中的`ToDoubleFunction`和`LongSupplier`等

## 异常的处理

### 1. 受检异常和非受检异常

受检异常指的是`Error`和`IOException`，非受检异常则是指`RuntimeException`，我们规定，如果是编程导致的错误，要抛出非受检异常，如常见的NPE；对于客观情况导致的异常，就要抛出受检异常，如FileNotFoundException。

经验丰富的开发者应该能看出来，使用者不用显示的catch非受查异常，却需要显示的catch和throw受检异常。正是因为这种设计，导致客户端不得不去在编译期就面对受检异常，好处是客户端可以及时恢复这个因客观原因导致的问题，这会使得程序变得更加健壮

### 2. 谨慎抛出受检异常

因为受检异常需要强制用户直面问题，如果过度使用受检异常，则会使得客户端的代码写超级多的模版代码，这降低了写代码的效率以及代码的可读性，这很有可能是得不偿失的

如果确实是由客观情况导致的异常且不需要为客户端提供详细的错误信息，不妨试试返回一个`Optional`

抛出受检异常的唯一CASE有两个条件：

1. 客观原因导致的失败
2. 客户端需要详细的失败信息

### 3. 创建和处理异常的一些TIPS

1. 创建异常时，要根据该异常的适用场景创建对应的构造方法，如`IndexOutOfBoundsException(int, int, int)`
2. 转换异常：根据封装性，客户端不应该感受到系统的实现细节，所以在系统实现的时候，如果遇到了底层的异常，往往需要进行转换成客户端可以理解的异常，然后rethrow
3. 记录异常：当发生异常时，往往需要将该异常记录下来，不过到底是记录整个异常堆栈还是异常的msg，这是一个根据场景不同而需要权衡的事情

## 并发

根据我的开发经验，在多线程并发过程中，一般有两种问题，一个是线程安全问题，另一个是线程通信问题。线程安全可以通过锁，`volatile`，`final`，copy副本以及线程局部变量的形式解决，而线程通信则可以通过`notify/wait`，`signal/await`之类的来解决

因为并没有在工作中过多设计到并发，所以这次也不赘述了