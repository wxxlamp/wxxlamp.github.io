---
title: Handling Multiple Business Scenarios in an MQ Consumer
date: 2021-07-19 22:36
tags:
  - 消息队列
  - 系统设计
categories:
  - 场景实践
description: >-
  Three design-pattern solutions for an MQ consumer overwhelmed by bizCode
  branches: strategy-based routing, an ordered chain of responsibility, and a
  template method for shared processing.
lang: en
translation_of: mq-a-consumer-biz-resolution
---

At heart, these are several ways to handle too many peer-level business branches in one scenario.

### Introduction

Many projects use message queues for asynchronous processing, which necessarily creates a consumer side. A listener may receive several topics or several `bizCode` values, each requiring different processing logic. The ordinary solution is a series of `if-else` branches:

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

This approach violates the open-closed principle: every additional business scenario requires another branch. It is fundamentally a case of **too many branches**. I came up with several alternatives.

### Strategy Pattern

When **one consumer listener** handles several `bizCode` values and each value corresponds to a different strategy, we can implement the strategy pattern through a table-driven design. A map routes topics to their handlers.

1. First, define a strategy interface.

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

2. Next, define a factory that loads strategies through a map.

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

3. Define the concrete default strategy.

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

4. The consumer can now use the factory directly.

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

### Chain of Responsibility

When **one consumer listener** handles several `bizCode` values, we can combine the chain-of-responsibility and template-method patterns to build a general consumer for multiple business scenarios.

Compared with the strategy pattern, this lets users **define the degree to which each handler supports different businesses**. A handler can support multiple businesses or none, return early, and so forth.

1. First, define the chain executor. It supports Spring's `@Order` annotation.

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

2. I want each handler to decide whether it terminates the chain, so the parameter includes an `over` flag.

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

3. Next, define the node-handler interface. Common processing is abstracted here using the template-method pattern.

   ```java
   public interface ChainHandler {
   
       void process(ChainParam param);
   
       boolean supports(ChainParam param);
   
       default boolean supports(BizCode code, ChainParam param) {
           return code.equals(param.getBizCode) && !param.isOver();
       }
   }
   ```

4. Finally, define a handler for a particular business.

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

5. To use the chain, the consumer only needs to inject `ChainExecutor`.

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

### Template Method Pattern

The first two approaches address one consumer processing several businesses. When several consumers process different topics, polymorphism can likewise extract the common parts of those topic consumers. This is where the template-method pattern applies:

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

For each topic, simply add a consumer subclass that implements this abstract class.

### Follow-up Thoughts

1. The chain-of-responsibility and strategy patterns can also be combined, giving each chain node several corresponding strategy handlers.
2. This design makes use of Spring's container-management capabilities.
