---
title: "MyBatis中实体类和关系的映射原理"
tags:
   - Mybatis
   - Java
categories:
   - 源码剖析
date: 2021-03-29 21:36
description: "借鉴MyBatis实现JDBC结果集到Java对象的自动映射工具，深入理解ORM框架的核心原理。"
---

这个东西我好久就想写了，之前在阿里实习时，所有MySQL的数据都会以D1的频率备份到ODPS上，而我负责的项目需要查询ODPS里面的数据，但是ODPS的Java SDK版本类似于JDBC一样配置多且难用，所以我就诞生了写一个针对于ODPS的工具类以方便后来者操作ODPS，在写的过程中，我发现最难的就是映射那一块，所以拖了好久，今天终于拿出时间来分析下这一块的东西。

### 预备工作

在聊Mybatis之前，还是要先说下传统的JDBC查询数据库的步骤：

```java
@Test
public void testJdbc() {
    String url = "jdbc:mysql://localhost:3306/myblog?user=root&……";
    try(Connection conn = DriverManager.getConnection(url)){
        Class.forName("com.mysql.cj.jdbc.Driver");
        String author = "coolblog.xyz";
        String date = "2018.06.10";
        String sql = "SELECT id, title, author, content, create_time" + " FROM article" + " WHERE author = '" + author
            + "' AND create_time > '" + date + "'";
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery(sql);
        List<Article> articles = new ArrayList<>(rs.getRow());
        while (rs.next()) {
            Article article = new Article();
            article.setId(rs.getInt("id"));
            article.setTitle(rs.getString("title"));
            article.setAuthor(rs.getString("author"));
            article.setContent(rs.getString("content"));
            article.setCreateTime(rs.getDate("create_time"));
            articles.add(article);
        }
        System.out.println("Query SQL ==> " + sql);
        System.out.println("Query Result: ");
        articles.forEach(System.out::println);
    } catch (ClassNotFoundException e) {
        e.printStackTrace();
    } catch (SQLException e) {
        e.printStackTrace();
    } 
 }
```

由上面的示例我们可以看到，使用JDBC的时候，我们首先需要注册数据库驱动，然后建立连接（此处可以通过连接池进行复用），然后通过该连接去打开执行SQL的`Statement`对象，通过`Statement`执行SQL，然后从返回值`ResultSet`中去获取对应的SQL结果。

而我们本章要探究的就是拿到SQL结果之后，我们如何**将`ResultSet`映射为我们的实体类**。

### 主要模块

首先看下Mybatis映射需要的主要模块：主要有一些`Wrapper`，`Handler`和`Configuration`来负责处理

`ResultSetHandler`：负责整次查询的主要映射工作

`ResultSetWrapper`：`ResultSet`的包装类，包含了`ResultSet`和该查询的列的meta info，如每个列的名字，每个列的Java类型，每个列的db类型，等等

`ResultHandler`：对结果集的自定义处理，默认放到list中，我们可以对其自定义DIY等等

`MappedStatement`：从mapper/*.xml或者注解中获取，存储每条sql的标签(如select，update)的状态

`ResultMap`：从`MapperStatement`中获得的结果集的映射方式，跟`resultMap`标签相对应

`TypeHandler`：从`ResultSet`中获得对应column的值

`MetaObject`：对实体类进行封装，除了`rowValue`之外，还有其他的数据元信息，如getter和setter等等。其实很多框架的实体类数据元信息都是和反射先关的

##### 模拟实现

为什么需要这么多类呢？我们可以换个角度来想，假如让我们做一个这个框架目前我们只有JDBC提供的`ResultSet`和要映射的Class。那么我们首先要对`ResultSet`进行包装，将常用的数据进行缓存，这个就是Mybatis中的`ResultWrapper`。接着，我们还应该对多行数据进行处理，此时，Mybatis把这个功能交给了`ResultHandler`。除此之外，我们还要知道实体类中的属性的Class，这是就用到了通过反射的setter方法获取，这个即是Mybatis中的`MetaObject`，同时，我们需要拿到自定义的映射方法，即是上文提到的`ResultMap`，最后，我们要把java的类型和数据库字段类型对应起来，这个就用到了我们下文提到的`TypeHandlerRegistry`

### 主要流程

其实ORM的映射主要分为两个过程：如将jdbcType和javaType按照不同db进行映射，然后将`propertyName`和`columnName`按照一定规则进行映射。对于前者来说，Mybatis主要是通过`TypeHandlerRegistry`里面的Map来完成映射的；对于后者来说，主要是通过`ResultSetHandler`来完成的

1. 当获得到`ResultSet`之后，创建出更适合框架进行解析的`ResultSetWrapper`，它记录了每一列的数目、类型等等，方便框架对其进行操作

2. 接着获得`ResultMap`，等会用于`propertyName`和`columnName`自定义规则的映射

3. 通过`ResultMap`中获得实体类的class，然后反射生成实体类对象rowValue，此时rowValue的每个属性为空。如果没有定义`ResultMap`时，则。。。。TODO

4. 将rowValue封装到`MetaObject`中，`MetaObject`同样是记录元信息，包括该类是不是有setter，getter之类的。`MetaObject`的作用就是为了第五步——获得javaType

5. 将自动映射（自动映射即column和property一模一样）的字段和自定义映射（即`ResultMap`配置文件）中的字段分别存放到两个map缓存中，并且通过setter和getter方法获得字段的javaType

   >这里我们要注意，自动映射的时候， 如何拿到一个属性的javaType是个问题，而Mybatis则是通过setter方法和getter方法来获取的。对于自定义映射来说，因为用到了`ResultMap`里面会记录的有

6. 生成`UnMappedColumnAutoMapping`对象，作用是将自动映射中的jdbcType和javaType对应起来，同时装有对应javaType的`TypeHandler`，`TypeHandler`的获得是通过我们之前提到过的`TypeHandlerRegistry`，至于`TypeHander`具体的作用，到第七步揭晓

7. 当我们拿到`UnMappedColumnAutoMapping`之后，我们要意识到，我们此时已经拿到了`columnName`以及其映射的`propertyName`，同时还拿到了`TypeHandler`，它的作用就是通过策略模式来完成不同javaType来获取数据库的字段

8. 此时，DB的一行数据已经映射完成了，那么如果是多行数据的话，它就会由`ResultHandler`进行处理

当然，上面只是一般的流程，Mybatis的映射还包含了offset的分页（性能比较低），嵌套映射等等

### 借鉴思路

设计类的时候，有很多wrapper，这些wrapper主要除了封装原来的类，还有其他的meta info，如配置信息，类加载器，有利于框架处理的信息等等，不过，这些额外信息都是可以通过原来类拿到的

很多框架都有context，也就是我们理解的上下文，可以理解为当前程序段的一些变量，对于Spring来说，`ApplicationContext`就存储这整个Spring容器的bean（回头写一篇如何获取bean文章）

获取属性的类型，可以通过bean的setter方法来获取

Mybatis在对`TypeHandler`处理时，主要用到了策略模式，它可以通过Map来实现











