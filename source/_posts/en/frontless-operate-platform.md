---
title: Building a Frontend-Free Operations Platform
date: 2021-09-19 22:38
tags:
  - 系统设计
  - 研发效能
categories:
  - 场景实践
description: >-
  A backend-oriented frontend-free operations platform that abstracts operations
  into four steps. Through annotations and the strategy pattern, backend
  developers only need to implement interfaces to generate operations pages
  automatically.
lang: en
translation_of: frontless-operate-platform
---

### Introduction

When a business grows rapidly from zero to one, many supporting operations tools cannot keep up. The frontend or backend team may have no resources to invest in an area with low initial ROI. Yet many infrequent scenarios still need a platform, such as:

1. Checking a user's status
2. Checking an order's status
3. Checking the current flow of a product
4. Quickly locating a customer's problem when a complaint arises, and so on

All of these examples require developers to query the database manually. So can we build such a platform quickly with minimal resources? Since I am a backend developer, I wanted to avoid dealing with frontend pages and develop only backend code. That is why this frontend-free operations approach was born.

### Principle

Why call it a frontend-free operations platform? Because it genuinely requires no frontend code.
Based on my abstraction of most operations platforms, most operations are one-off actions. Unlike a business system, where users need to complete many workflows, operations-platform users usually perform an action only once (for example, querying a customer's information or correcting a piece of data). We can therefore understand an operations lifecycle as one action, and one action contains four corresponding parts: **operation type, operation input, operation method, and operation output**.

I abstracted the operations platform into four operations:

1. Obtain the operation type.
2. Obtain the fields to enter according to the operation type.
3. Execute the operation.
4. Obtain the output corresponding to the operation.

Once these four steps are fixed in the frontend, users only need to define the four operations in the backend to implement the required operations logic.

### Problems and solutions

The four steps above are enough to complete the operations logic. The problem becomes how to express the user's logic in a programming language. Each step presents challenges.

#### 1. Obtaining the operation type

There are two options for storing operation types:

1. Put user-defined operation types in a List array.
2. Put user-defined operation types and their corresponding operation Handlers in a Map. ✅

There are also several options for registering operation types:

1. Use a system interface that requires users to return the type of an operation.
2. Use file configuration that requires users to explicitly write the operation type.
3. Use annotations so users configure the operation type in the corresponding operation Handler. ✅

#### 2. Obtaining input fields

The input parameters differ for every operation. How does the system obtain the fields and properties of each operation's input?

1. Define an interface requiring users to return input properties (such as whether a field is required and what is shown to customers), then parse them during initialization and return them to the frontend at execution time.
2. Use file configuration to configure the properties of an operation's input fields.
3. Define annotations so users configure field properties with annotations on the field types. ✅

#### 3. Executing an operation

There are several questions during execution.
**First, how do we convert the frontend's untyped structure into Java's strong types?**

1. Have the frontend pass a map.
2. Since the backend can obtain the input class through an interface or generic type, instantiate it directly with reflection and fill in its values.

**Second, how do we convert the user's custom output into an output the system can recognize?**

1. Use reflection to obtain the existing values of the corresponding system fields.
2. Combine the user's configured annotations with the existing system output structure and fill it in.

#### 4. Standardizing custom handlers

1. Restrict them through an interface. ✅
2. Mark the handler method with a method-level annotation.

### Implementing the flow

#### 1. Initial system work

##### Parsing

After each configuration bean is initialized, its input and output configuration is parsed.

1. Obtain the actual input and output types through generics.
2. Parse the input/output configured by the user through annotations into the system's internally defined input/output data structures.
3. Obtain the `OperationType` configured through annotations for each configuration class.
4. Validate annotations on inputs and outputs to constrain user behavior.

##### Registration

The strategy pattern and Spring's capabilities are used to register the Bean in the system map after Spring initialization.

1. If the bean type is `OperationConfig`, the system looks for that class's `OperationType`.
2. It registers `ope` as the key and `config` as the value in the map.

#### 2. System execution flow

##### Obtaining the operation type

* Obtain it directly from the `OperationType` registered earlier.

##### Obtaining request parameters

* Obtain them directly from the input data structure parsed earlier.

##### Executing the operation

1. Convert the parameters sent by the frontend into a user-defined input instance **[key point]**.
2. Call the user's business operation through the interface.
3. Convert the user's custom output into the system's internal output structure **[key point]**.
4. Wrap the completed internal output structure into a response and send it to the frontend.
5. Render the formatted response on the frontend.

#### 3. System flow diagram

The system loads, parses, and renders the data structure from compilation time through runtime.

> One additional point: common middleware such as Spring and Mybatis generally follows these steps:
> 1. First standardize the user's custom data structures (for example, Spring and Mybatis both require users to define XML or annotations).
> 2. When the program starts, load and identify the user's data structures and convert them into the middleware's own structures (such as Spring's `BeanDefinition`).
> 3. Once the program is running, calculate based on different user requests and the existing data structures. (This calculation completes the middleware's main function.)

From the user's custom data structures to the system rendering them as frontend pages, the process roughly follows these steps:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/e98aac17_frontless-operate-platform.jpg" align="middle" />

### Other considerations
#### 1. Caching
Reflection is relatively expensive, so several additional fields are defined to store reflection metadata. **[Trade space for time]**
#### 2. Composition over inheritance
Use composition to limit the user's operating space and improve system robustness.
#### 3. Converting strong and weak types
Weak type to strong type:

1. map -> reflection
2. JSON -> deserialization

Strong type to weak type: (none)
