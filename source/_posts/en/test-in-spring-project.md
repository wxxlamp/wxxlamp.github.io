---
title: Unit and Integration Testing in Spring Projects
tags:
  - Spring 框架
  - 测试与质量
categories:
  - 场景实践
date: 2023-02-18 19:36
description: >-
  Explains unit-testing and integration-testing practices in Spring projects,
  including JUnit, Mockito, and PowerMock, along with configuration strategies
  for data sources, external RPC-interface mocks, and test containers.
lang: en
translation_of: test-in-spring-project
---

## Overview

By scope, system testing is roughly divided into unit testing, integration testing, regression testing, and so on. Usually, the testing developers are truly responsible for includes unit testing and integration testing.

In actual development, people understand the scope of different tests differently. In this article, unit testing generally means testing at class or module granularity, while integration testing means testing all business logic under an API at API granularity.

A unit test is a test of one class’s business logic. Before testing, all downstream dependencies and modules of that class need to be MOCKed, and different cases need to be created for different test scenarios, thereby ensuring the correctness of the class’s business logic.

An integration test is a test of a business process. It does not test one module or one class; it tests correctness among all classes and modules in a business flow.

### Unit vs. integration
Unit tests have many advantages. For example, they are very quick to write: we only need to test the code for which we are responsible. Even without familiarity with the whole application code, we can write robust test code.

But if we must take responsibility for all business logic, we have to write integration tests. They let us refactor more boldly and help new colleagues understand business code faster. Moreover, because integration tests target business logic rather than modules, even if we add classes or modules for a business flow, existing integration-test cases alone can test the incremental code.

Integration tests also have one drawback: the application’s dependent integration infrastructure and external dependencies need to be mocked, requiring enormous early effort. But once integration testing covers an application, it is work that benefits both the present and the future.

### Easily confused concepts
#### Junit&Mockito&PowerMock

Quoting ChatGPT directly:

> JUnit is one of the most popular testing frameworks in Java, primarily used to write unit tests. It provides basic assertions and test annotations for testing various parts of Java applications.
> Mockito is a Mocking framework for Java that lets you replace real objects with mock objects and simulate method calls and object state in unit tests.
> PowerMock is a Mocking framework based on Mockito and EasyMock. It lets you mock static methods, constructors, private methods, and similar items that are normally difficult to mock in unit tests.
> Therefore, JUnit is used to write unit tests, Mockito to mock objects, and PowerMock to mock static methods, constructors, private methods, and similar items.

## Unit testing
In general, writing good unit tests is comparatively simple. When testing a class, it is generally not recommended to start the Spring container. Doing so initializes many Beans that do not need testing and makes UT startup very slow. If the Spring container is started, many unnecessary Beans must be mocked too, resulting in very low ROI.

Therefore, the examples below do not use container-based testing; they test without starting the container at all.
### Simple test
If the class to test is very simple and has no dependency on other external classes, we only need to include the Junit package and write the following code:
```java
public class Test {

    @Test
    public void test() {
        Assert.assertEquals(StringUtils.substring("aaabbb", 0, 3), "aaa");
    }
}
```
In reality, this type of test is rare. It may be used only when testing utility classes without downstream dependencies. More often, a class under unit test has many downstream dependencies, so how should it be tested?
### Dependency test
Suppose we have the following class:
```java
public class TestDependency {

    private TestSimple testSimple = new TestSimple();

    public String runDependency() {
        return testSimple.getName();
    }
}
```
If we want to test only `TestDependency` without depending on the original `TestSimple`, we can use Mockito and PowerMock, injecting a mock of `TestSimple`, as follows:
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
> Note: with a Spring container, there is another way to mock, which is not discussed here.

#### Mock&InjectMocks&Spy
When starting with PowerMock, people often have questions about these three mocking methods. Here is an explanation:

1. [Both Mock and Spy can mock objects (in Chinese)](https://www.cnblogs.com/zendwang/p/mockito-mock-spy-usage.html). For methods whose mocks are not specified, Spy calls the real method by default and returns its real return value; Mock does not execute it by default and returns null even where there is a return value. Therefore, in theory, using Spy gives higher unit-test coverage.
2. InjectMocks can create an instance. Simply put, this Mock can call methods in real code. We generally use InjectMocks to mark the real object to test.

### Module testing
Sometimes we want to test not just one class, but multiple classes continuously or a whole module. Without the Spring container, this is difficult with InjectMocks. Consider this example:
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
Suppose in one UT I want to test both `TestDependency` and `TestSimple`, mocking only `TestInner`. In theory this is difficult with InjectMocks. One approach is constructor injection. (*Spring does not recommend injection through Autowired), as follows:
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
The test can then be written this way. This is also a reason Spring recommends constructor injection:
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
### Mocking static methods
Sometimes testing requires mocking a static utility class. In this case, the two methods above are unsuitable. We need PowerMock’s capability, using `@PrepareForTest` to mock these utility classes, as follows:
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
### Mocking private methods
Sometimes even the behavior of private methods is uncertain, so they need to be mocked. PowerMock can still mock and stub private methods here.
~~Omitted~~

## Integration testing
Integration testing differs from unit testing. Generally, we need to test all business logic, and one business flow basically contains most code. Thus integration testing generally starts a Spring test container, mocks external RPC, middleware Beans, and databases, and runs all other code through real logic.

### SpringTest vs SpringBootTest
When testing a Spring container, there are commonly two configurations. One tests only the Spring container:
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
The other tests a SpringBoot container:
```java
@RunWith(SpringRunner.class)
@SpringBootTest
public class SpringTest {
    @Autowired
    private JdbcTemplate jdbcTemplate;
}
```
Since SpringBoot adds auto-configuration, the difference is that the first only tests the Spring container, while the second introduces SpringBoot’s configuration capability. For a simple example, if `JdbcTemplate` is included in a test class, the first approach cannot obtain it; only SpringBootTest can obtain the automatically configured Bean.

In other words, when testing with the Spring container, we need additionally to mock many Beans automatically configured in SpringBoot. But that also has an advantage: we can choose which Beans to include instead of allowing SpringBoot auto configure to include every configuration Bean.

Furthermore, SpringBootTest automatically scans test configuration classes, unlike a Spring container, which uses `ContextConfiguration` to bring in configuration.
### Data-source Mock
A data-source Mock means mocking database-related operations. This allows repo and specific SQL to be tested, giving higher code coverage.

Generally, an H2 in-memory database replaces a remote MySQL database when mocking a data source. In addition, if IDs are generated with sequences, the corresponding base classes must be mocked.

But mocking only `DataSource` is not enough. As mentioned above, if we use only Spring-container testing, we also need to reinject other classes depending on data Source, such as `SqlSessionFactoryBean `, `PlatformTransactionManager `, and `TransactionTemplate `.

If we use SpringBootTest, other Beans need not be reinjected, as follows:
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
### External-interface Mock
External RPC interfaces also need mocking for integration tests. With the Spring container, there are two ways. Interfaces whose expected value is the same in every case can be mocked uniformly; interfaces requiring different expected returns in different cases—for example a risk-control interface where successful and failed paths must be tested—need customized mocks.
#### Uniform MOCK
There are three ways to mock uniformly:

1. Implement the interface directly
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

2. If an interface has too many methods and we do not want to implement them all, Mockito can mock a specific method.
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

3. Or, if we only want to mock the Bean and do not need its return value, Mockito can do this too:
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

#### Customized MOCK
On the basis of unified external mocks, Mockito can customize mocks for different cases in different UTs, as follows:
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
That said, these customized mocks are recommended to be wrapped in one class. From a design-pattern perspective, composition is better than inheritance.

### Infrastructure Mock
Beyond external services, infrastructure such as encryption/decryption, MQ, and caching also needs mocking. The approaches are broadly the same, so they are not repeated here.
### Excluding and including Beans
Above we introduced many mock Beans. The container may fail to start because it can contain both real and mock Beans. In that case, conflicting real Beans need to be excluded from the test container.

In addition, some Beans load unpleasant things that prevent the test container from starting, so they need exclusion as well:
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
