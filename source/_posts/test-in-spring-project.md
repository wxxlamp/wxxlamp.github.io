---
title: "Test In Spring Project"
tags:
   - Spring
categories:
   - 场景实践
date: 2023-02-18 19:36
description: "Spring项目中的测试实践指南，涵盖单元测试和集成测试的方法论与常用工具。"
---

## 概述

系统的测试，从范围大致会分为单元测试，集成测试，回归测试等等。通常来说，真正由开发所负责的测试包含单元测试和集成测试。
由于大家在实际的开发过程中，对各种测试的范围理解都不一样，就本文来讲，一般说的单元测试指（按照类维度/模块维度），集成测试是以接口维度对该接口下的整个业务逻辑进行的测试
所谓单元测试，就是对某个类业务逻辑的测试，在测试之前，需要将该类所依赖的下游和模块全部MOCK掉，并且根据测试场景生成不同的case，从而保证类的业务逻辑的正确性。
所谓的集成测试，是对业务流程的测试，它不是对一个模块或者一个类的测试，而是测试某个业务流程下，所有类和模块之间的正确性。

### 单元VS集成
单元测试的优点有很多，譬如编写起来非常快，我们只要对负责自己编写的代码进行测试即可，即使我们在不熟悉整个应用代码的情况下，也可以写出很健壮的测试代码。
但是如果要对整个业务逻辑负责，就不得不写集成测试，集成测试可以帮助我们更大胆的重构，同时，也可以方便新同学更快的了解业务代码，除此之外，因为集成测试是针对业务逻辑而非模块的，所以即使我们针对于某业务逻辑新增了一些类或者模块，我们甚至只依赖于老的集成测试的用例，就可以测试到增量的代码。
不过集成测试也有一个缺点，就是需要对应用以来的集成设施和外部以来进行mock，这在前期需要付出极大的精力去完成这件事情。不过一单集成测试覆盖到应用之后，就是一件功在当代，利在千秋的事情。
### 傻傻分不清的概念
#### Junit&Mockito&PowerMock

直接引用chat-gpt的回复：

> JUnit是Java中最流行的测试框架之一，主要用于编写单元测试。它提供了一些基本的断言和测试注释，用于测试Java应用程序的各个部分。
> Mockito是一个用于Java的Mocking框架，它允许您使用模拟对象替换真实对象，并在单元测试中模拟方法调用和对象状态。
> PowerMock是一个基于Mockito和EasyMock的Mocking框架，它允许您在单元测试中模拟静态方法、构造函数和私有方法等内容，这些通常是很难模拟的。
> 因此，JUnit用于编写单元测试，Mockito用于模拟对象，而PowerMock用于模拟静态方法、构造函数和私有方法等内容。

## 单元测试
一般来说，写好单元测试，相对来说简单一点。同时，如果在测试类的时候，一般是不建议启动Spring容器的，这样会把很多不需要测试的bean也初始化进来，会导致UT的启动时间变得很长。同时，如果启动了Spring容器，要把很多不需要测试的bean进行mock，这样的ROI也非常低。
所以在下面的示例中，我没有列出来Spring容器的测试方式，而是使用完全不启动容器的方式来进行测试。
### 简单测试
如果我们要测试的类非常简单，也没有依赖其他外部类，那么我们只需要引入Junit包，同时编写如下代码即可：
```java
public class Test {

    @Test
    public void test() {
        Assert.assertEquals(StringUtils.substring("aaabbb", 0, 3), "aaa");
    }
}
```
但是事实上，这种测试非常少，只有在测试没有下游依赖工具类的时候可能会用到。除此之外，在单元测试中，我们要测试的类，更多是有很多下游依赖的，那么这种情况该怎么测试呢？
### 依赖测试
假如说是下面的一个类：
```java
public class TestDependency {

    private TestSimple testSimple = new TestSimple();

    public String runDependency() {
        return testSimple.getName();
    }
}
```
如果我们想只测试`TestDependency`而不想依赖原始的`TestSimple`，那么我们就可以使用Mockito和PowerMock，通过对TestSimple进行注入mock的方式进行测试，如下所示：
```java
@RunWith(PowerMockRunner.class)
public class TestDependencyTest {

    @InjectMocks
    private TestDependency testDependency;

    @Mock
    private TestSimple testSimple;

    @Test
    public void test() {
        Mockito.when(testSimple.getName()).thenReturn("B");
        Assert.assertEquals("B", testDependency.runDependency());
    }
}
```
> 注意，如果是Spring容器的话，还有另外一种mock方式，这里暂时不表。

#### Mock&InjectMocks&Spy
如果刚开始使用PowerMock，往往会对这三种mock方式有疑问，下面做一个说明：

1. [Mock和Spy都可以对对象进行mock](https://www.cnblogs.com/zendwang/p/mockito-mock-spy-usage.html)，但是对于未指定mock的方法，spy默认会调用真实的方法，有返回值的返回真实的返回值，而Mock默认不执行，即使有返回值的，也默认返回null；所以理论上讲，使用Spy的话，单测的覆盖率会更高一点
2. InjectMocks可以创建一个实例，简单的说是这个Mock可以调用真实代码的方法，我们一般会通过InjectMocks来标注真实的要测试的对象


### 模块测试
事实上，有时候我们不单单想测试一个类，如果要连续测试多个类或者一整个模块的话，在不使用Spring容器的情况下，用InjectMocks就比较困难了，举个下面的例子：
```java
public class TestDependency {

    private TestSimple testSimple = new TestSimple();

    public String runDependency() {
        return testSimple.getName();
    }
}
public class TestSimple {

    public TestInner testInner = new TestInner();

    public String getName() {
        return testInner.getName();
    }
}
public class TestInner {
    public String getName() {
        return "a";
    }
}
```
假如说我在一个UT中，既想测试`TestDependency`和`TestSimple`，只mock`TestInner`的话，理论上用InjectMocks是比较困难的，这个时候有一个方法，就是通过构造方法的注入来实现。（*Spring不推荐通过Autowired注入），如下所示：
```java
public class TestDependency {

    private final TestSimple testSimple;

    public TestDependency(TestSimple testSimple) {
        this.testSimple = testSimple;
    }

    public String runDependency() {
        return testSimple.getName();
    }
}
public class TestSimple {
    
	private final TestInner testInner;

    public TestSimple(TestInner testInner) {
        this.testInner = testInner;
    }

    public String getName() {
        return testInner.getName();
    }
}

public class TestInner {
    public String getName() {
        return "a";
    }
}
```
这样的话，我们的测试方法就可以这么写，这也是Spring推荐构造器注入的一个理由
```java
@RunWith(PowerMockRunner.class)
public class TestDependencyTest {

    private TestDependency testDependency;

    @Mock
    private TestInner testInner;

    @Test
    public void test() {
        Mockito.when(testInner.getTestInner()).thenReturn("BC");
        testDependency = new TestDependency(new TestSimple(testInner));
        Assert.assertEquals("BC", testDependency.runDependency());
    }
}
```
### Mock静态方法
有时候，我们在测试时需要将静态的工具类mock掉，在这种情况下，前面两种方式就不太合适，我们需要借助PowerMock的能力，通过`@PrepareForTest`注解，将这些工具类mock掉，如下所示：
```java
@RunWith(PowerMockRunner.class)
public class TestSimpleTest {

    @Test
    @PrepareForTest(StringUtils.class)
    public void testA() {
        PowerMockito.mockStatic(StringUtils.class);
        Mockito.when(StringUtils.substring(Mockito.anyString(), Mockito.anyInt(), Mockito.anyInt()))
            .thenReturn("a");
        Assert.assertEquals("a", StringUtils.substring("AAAAA", 0,3));
    }

}
```
### Mock私有方法
甚至有时候，对于某些私有方法的行为，也是不确定的，所以我们也需要去mock它，这个时候，我们仍然可以通过PowerMock去完成私有方法的Mock和打桩
~~略~~

## 集成测试
集成测试和单元测试不一样，一般来说，我们需要测试整个业务逻辑，而一个业务逻辑中基本就包含了大部分的代码，所以对于集成测试来讲，我们一般都会直接启动一个Spring的测试容器，将外部的RPC，中间件的bean和数据库进行mock，除此之外，其他的代码都会走到真实的逻辑当中。

### SpringTest vs SpringBootTest
在测试spring容器的时候，往往有两种配置，一种是单纯测试Sring容器：
```java
@RunWith(SpringRunner.class)
@ContextConfiguration(classes = {TestDataSourceConfig.class},
        loader = AnnotationConfigContextLoader.class)
@TestPropertySource(locations = {"classpath:test.properties"} )
public class SpringTest {
	@Autowired
    private JdbcTemplate jdbcTemplate;
}
```
另外一种是测试SpringBoot容器：
```java
@RunWith(SpringRunner.class)
@SpringBootTest
public class SpringTest {
    @Autowired
    private JdbcTemplate jdbcTemplate;
}
```
因为SpringBoot多了自动装配的能力，所以这两者的区别就是，第一种是只测试Spring容器，而第二种会引入SpringBoot的装配能力。举个简单的例子：
如果我们在测试类中引入`JdbcTemplate`这个bean的话，使用第一种方式是获取不到的，只有通过SpringBootTest才能拿到自动装配的bean。
换句话说，如果使用spring容器来测试，我们需要额外mock很多在SpringBoot中自动装配的bean。但是这样也有一个优点，就是我们可以自己选择引入哪些bean，不用通过SpringBoot的auto configure将所有的配置bean全都引入进来。
除此之外，SpringBootTest还可以自动扫描测试的配置类，而不是像Spring容器一样，通过`ContextConfiguration`来完成配置项的引入。
### 数据源Mock
所谓的数据源Mock，就是需要mock数据库相关的操作。这样就可以测试到repo和具体的sql，使代码的覆盖度更高。
一般来讲，Mock数据源的话，我们需要通过H2内存数据库来代替远程的Mysql数据库。除此之外，如果是用到sequence生成id的方式的话，我们也需要将对应的基础类进行mock。
但是我们不能只mock`DataSource`就认为是万事大吉了，就像上文所说，如果我们只用了Spring容器的测试，我们就还需要将依赖data Source的其他类进行重新注入，譬如`SqlSessionFactoryBean `、`PlatformTransactionManager `、`TransactionTemplate `等等。
而如果我们使用了SpringBootTest的测试，就无需对其他bean进行重新注入。如下所示：
```java
@TestConfiguration
public class TestDataSourceConfig {

    @Bean(name = "dataSource")
    public DataSource dataSource() {
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .setName("testDB")
            .addScript("classpath:db/init.sql")
            .build();;
    }
}
```
### 外部接口Mock
对于外部的rpc接口来说，我们在做集成测试的时候也需要将其mock掉。就Spring容器来说，我们有两种mock方式，对于那些不管在什么case下，期望值都一样的接口，我们可以统一mock掉；而对于那些不同case需要期待不通返回值的（譬如风控接口，我们需要测试其返回成功或者失败的链路），我们就需要定制化mock。
#### 统一MOCK
统一mock的方式有两种，如下所示：

1. 直接实现接口
```java
@TestConfiguration
public class ServiceMockConfig {
    @Bean
    public ExtRpc extRpcMethod() {
        return new ExtRpc() {
            @Override
            public ExtRpcResponse query(ExtRpcRequest request) {
                ExtRpcResponse response = new ExtRpcResponse();
                response.setSuccess(true);
                return response;
            }
        };
    }
}
```

2. 如果接口中包含的方法太多，我们不想全部都实现完，我们可以通过Mockito完成特定方法的mock
```java
@TestConfiguration
public class ServiceMockConfig {
    @Bean
    public ExtRpc extRpcMethod() {
        return Mockito.mock(ExtRpc.class, e -> {
            String method = e.getMethod().getName();
            switch (method) {
                case "query":
                    ExtRpcResponse response = new ExtRpcResponse();
                    response.setSuccess(true);
                    return response;
                default:
                    return null;
            }
        });
    }
}
```

3. 又或者，我们只是想mock这bean，也不需要感知到它的返回值，那么我们也可以通过Mockito完成：
```java
@TestConfiguration
public class ServiceMockConfig {
    @Bean
    public ExtRpc extRpcMethod() {
        return Mockito.mock(ExtRpc.class);
    }

    /**
    * 不推荐，因为IDEA不能识别
    */
    @MockBean
    public ExtRpcA extRpcA;
}
```

#### 定制化MOCK
我们可以在外部统一mock的基础中，通过mockito对不通UT的不同case完成定制化的mock。如下所示：
```java
public class RpcMock {

    public static void mockRpcExt(boolean ans) {
        Mockito.doReturn(buildMockRpcResponse(ans)).when(InstanceLocator.getInstance(ExtRpc.class)).query(Mockito.any());
	}
    private static ExtRpcResponse(boolean ans) {
        ExtRpcResponse response = new ExtRpcResponse();
        response.setSuccess(ans);
        return response;
    }
}

@RunWith(SpringRunner.class)
@ContextConfiguration(classes = {TestDataSourceConfig.class},
        loader = AnnotationConfigContextLoader.class)
public class Test {
    @Before
    public void init() {
        RpcMock.mockRpcExt(true);
    }
}
```
不过要说的是，这里推荐将这些定制mock封装在一个类里，毕竟从设计模式上讲，组合大于继承。

### 基础设施Mock
除了外部服务之外，我们还需要对一些基础设施进行mock，譬如加解密，MQ，缓存，等等，总体上来说都是异曲同工的，所以这里就不赘述了。
### Bean的排除和引入
上文我们引入了很多mock的Bean，容器很有可能会启动不起来，因为可能此时容器中既有真实的Bean，又有mock的Bean，这个时候，我们就需要将那些冲突的真实的Bean从测试容器中排除。
除此之外，有些Bean因为加载了非常恶心的东西（导致我们测试容器启动不起来），我们也需要排除。如下所示：
```java
@ComponentScan(basePackages = {
    "扫描我们希望引入的包和类"
}, excludeFilters = @ComponentScan.Filter(type = FilterType.ASSIGNABLE_TYPE,
        classes = {要排除的包和类}))
@Import({
        希望引入的bean
})
@TestConfiguration
public class ServiceMockConfig {}
```