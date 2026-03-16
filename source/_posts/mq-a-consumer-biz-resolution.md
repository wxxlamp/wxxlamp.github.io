---
title: "MQ消费多业务场景的实践"
date: 2021-07-19 22:36
tags:
   - Spring
   - MQ
categories:
   - 场景实践
description: "针对MQ消费端多bizCode分支泛滥问题，介绍三种设计模式解决方案：策略模式实现路由分发，责任链模式支持自定义顺序，模板方法模式抽象公共流程，可按场景灵活选用。"
---

本质上是场景层面上的对同级业务分支过多的几种解决方案

### 引言

在很多项目中都会用到消息队列来做异步处理，那么必然会有消费者的一方。大多数时候，我们监听的消息可能包含多种topic，或者是多种bizCode，不同的bizCode需要多种处理逻辑，普通情况下，我们需要多个if-else来处理问题，如下：

```java
@Service
public class Subscriber implements MessageListenerConcurrently {

    @Override
    public ConsumeConcurrentlyStatus consumeMessage(final List<MessageExt> msgs,
                                                    final ConsumeConcurrentlyContext context) {
        for (MessageExt msg : msgs) {
            try {
                String messageBody = new String(msg.getBody(), "UTF-8");
                Param param = JSON.parseObject(messageBody, Param.class);
              	BizCode code = param.getBizCode();
                if(BizCode.CODE_A.equals(code)) {
                  // doSomething
                } else if(BizCode.CODE_B.equals(code)) {
                  // doSomething
                } else {
                  // doSomething
                }
            } catch (UnsupportedEncodingException e) {
                return ConsumeConcurrentlyStatus.RECONSUME_LATER;
            }
        }
        return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
    }
}
class Param {
  private Object bean;
  private BizCode code;
}
```

但是这种if-else不符合设计原则中的开闭原则，有多少个业务场景，我们就必须要增加多少个分支来处理。本质上是**分支过多的场景**。就此来说，笔者想到了几种方案来处理：

### 策略模式

在**只有一个消费者监听**多种bizCode的场景下，假如说不同bizCode对应着不同的策略，那么我们就可以借用表驱动的方式来实现策略模式，通过map路由不同的topic和对应的handler

1. 首先定义一个策略接口

   ```java
   public interface StrategyHandler {
   
       /**
        * 监控处理器
        * @param bean
        */
       void handle(StrategyParam param);
   
       /**
        * 支持的业务码
        * @return bizCode
        */
       BizCode supportBiz();
   }
   ```

2. 接着定义加载策略的工厂(通过map)

   ```java
   @Component
   public class HandlerFactory implements BeanPostProcessor {
   
       private static Map<BizCode, StrategyHandler> HANDLER_CACHE = new HashMap<>(16);
   
       public static StrategyHandler getHandler(BizCode code){
           return HANDLER_CACHE.getOrDefault(code, DefaultHandler.INSTANCE);
       }
   
       @Override
       public Object postProcessBeforeInitialization(Object o, String s) throws BeansException {
           return o;
       }
   
       @Override
       public Object postProcessAfterInitialization(Object o, String s) throws BeansException {
           if(o instanceof StategyHandler){
               StategyHandler handler = (StategyHandler)o;
               HANDLER_CACHE.put(handler.supportBiz(),handler);
           }
           return o;
       }
   }
   
   ```

3. 定义具体的默认策略

   ```java
   @Service
   public class DefaultHandler implements StategyHandler {
   
     	/**
     	 * singleton
     	 */
       public static final DefaultHandler INSTANCE = new DefaultHandler();
   
       @Override
       public void handle(Param bean) {
           //do nothing.
       }
   
       @Override
       public BizCode supportBiz() {
           return BizCode.CODE_DEFAULT;
       }
   }
   ```

4. 消费者直接使用即可

   ```java
   @Service
   public class Subscriber implements MessageListenerConcurrently {
   
       @Override
       public ConsumeConcurrentlyStatus consumeMessage(final List<MessageExt> msgs,
                                                       final ConsumeConcurrentlyContext context) {
         // ...
         Param param = JSON.parseObject(messageBody, Param.class);
         HandlerFactory.getHandler(param.getBizCode()).handle(param);
         // ...
       }
   }
   ```

### 责任链模式

在**只有一个消费者监听**多种bizCode的场景下，我们可以结合责任链和模版方法模式，来打造一种通用的，多业务的消费场景。

相对于策略模式，它的优点在于用户可以**自定义对不同业务的支持程度**，可以支持多种业务，或者一种业务也不支持，也可以提前retrun等等其他优点。

1. 首先定义责任链执行器，责任链执行器支持Spring中的`@Order`注解

   ```java
   @Component
   public class ChainExecutor {
   
       @Autowired
       List<ChainHandler> handlerList;
       
       @PostConstruct
       public void init() {
           handlerList.sort(AnnotationAwareOrderComparator.INSTANCE);
       }
   
       public void process(Chain param) {
           // 按照@Order顺序排序
           if (CollectionUtils.isEmpty(handlerList)) {
               handlerList.forEach(e -> {
                   if (e.supports(param)) {
                       e.process(param);
                   }
               });
           }
       }
   }
   ```

2. 对于责任链来说，我希望每个执行器可以自定义自己是否为最终执行器，所以参数加了一个over标识

   ```java
   public class ChainParam {
     /**
      * 责任链是否终结
      */
     boolean over = false;
     
     /**
      * Meta传递来的业务bean
      */
     Object bean;
     
     /**
      * 业务码
      */ 
     BizCode bizCode;
   }
   ```

3. 接着，定义责任链中的节点处理器接口，同时，将一些公共的处理抽象出来，即此处用了模版方法模式

   ```java
   public interface ChainHandler {
   
       void process(ChainParam param);
   
       boolean supports(ChainParam param);
   
       default boolean supports(BizCode code, ChainParam param) {
           return code.equals(param.getBizCode) && !param.isOver();
       }
   }
   ```

4. 最后，定义特定的业务处理器即可

   ```java
   @Service
   public class SampleHandler implements ChainHandler {
   
       @Override
       public void process(ChainParam param) {
           // do some thing
       }
   
       @Override
       public boolean supports(ChainParam param) {
           return supports(BizCode.CODE_A, param);
       }
   }
   ```

5. 对于使用的话，消费者只需要注入 `ChainExecutor`即可

   ```java
   @Service
   public class Subscriber implements MessageListenerConcurrently {
   
       @Autowired
       private ChainExecutor executor;
   
       @Override
       public ConsumeConcurrentlyStatus consumeMessage(final List<MessageExt> msgs,
                                                       final ConsumeConcurrentlyContext context) {
         // ...
         ChainParam param = JSON.parseObject(messageBody, ChainParam.class);
         executor.process(param);
         // ...
       }
   }
   ```

### 模版方法模式

前面两种方案都是针对一个消费者消费多种业务的场景，那么当多个消费者消费不同topic的时候，我们是否也可以通过多态的形式，将多个topic的消费者共性的地方抽象出来呢？这就会用到我们的模版方法模式：

```java
public abstract class AbstractSubscriber<Bean> implements MessageListenerConcurrently {

    @Override
    public ConsumeConcurrentlyStatus consumeMessage(final List<MessageExt> msgs,
        final ConsumeConcurrentlyContext context) {
        for (MessageExt msg : msgs) {;
            Bean bean = null;
            try {
              bean = convertBean(new String(msg.getBody(), "UTF-8"));
              process(bean);
            } catch (Exception e) {
                return ConsumeConcurrentlyStatus.RECONSUME_LATER;
            }
        }
        return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
    }

    /**
     * 业务处理逻辑
     *
     * @param Bean
     * @return 成功或失败
     */
    protected abstract boolean process(Bean bean);

    /**
     * 将消息转换为实体类
     *
     * @param message
     * @return bean
     */
    protected abstract Bean convertBean(String message);
}
```

对于不同的topic，我们只需要添加不同的子类消费者实现该抽象类即可

### 后续

1. 我们也可以将责任链模式和策略模式结合起来，即每个责任链节点都有对应的多个策略Handler
2. 此处借助了Spring中容器管理的能力