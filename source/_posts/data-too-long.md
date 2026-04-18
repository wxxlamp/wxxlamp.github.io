---
title: "字段超过数据库范围的重构方案"
tags:
   - 数据库
categories:
   - 场景实践
date: 2020-11-01 10:36
description: "解决Oracle varchar2字段超4000字节上限问题，采用新建EXT扩展表以链表串联分片数据，通过代理模式实现最小侵入式改造。"
---

在公司实习的时候，发现因为历史遗留问题，在新需求中insert db的时候插不进去数据，查看堆栈报错的时候发现是因为Oracle的varchar只能存储4000Bytes，显然是超出范围了，那么需要找到一种方法去解决这个问题。

这篇文章记录下我的思考，不一定是最优解。

<!-- more -->

### 1. 方案调研

要存储的字段超过了数据库字段的范围，有如下几种解决方案：

1. 更改数据库字段的类型的存储范围 ——大字段容易造成性能问题
2. 数据库字段类型不变，把数据库中存为索引，指向其他地方（如数据库，文件等）——  会引起数据库结构的改变
3. 在插入的时候拆分字段，之后插入到表中——拆分字段再插入的话，因为每一行都有唯一Id，在不改变表结构的情况下，很难判断哪两行是之前未拆分的字段；而且这样有违之前数据库设计时的语义

### 2. 方案确定

经过综合考量，为了不影响数据库的语义，所以新建了一个数据库，用来存储溢出的字段：

```sql
CREATE TABLE EXT
(
id int not null primary key,
ext varchar not null,
next_id int,
belong varchar,
create_time timestamp
)
```

通过这个表，理论上在行数允许的情况下，容量就不再是问题（不考虑频繁查询性能的前提下）

那么下一个要解决的问题就是，如何尽可能小的侵入原有的代码：

在原始代码逻辑中，会有`service.insert(Domain)`和`service.query(Id)`两个逻辑，重点是如何无侵入地使这两个方案向往常一样使用。

在这里我使用了一个工具类，在insert之前会去判断字段是否过长，在query之后，会去判断是否使用了EXT的数据库。可以使用代理模式代理service类，从而增强insert和query的功能，也可以增加一个过滤器或者拦截器对insert和query进行拦截，然后处理

```java
@Component
public class ExtComponent {
	
	private static final Logger LOGGER = LoggerFactory.getLogger(ExtComponent.class);
	private static final String TO_EXT = "TO_EXT";
	private static final Integer MAX_VALUE = 1000;
    
    @Autowired
    private ExtMapper extMapper;
    
    /**
     *  1. 判断body是否字段过大，如果过大，则插入另一个表
     *  2. 插入的过程是循环插入（Java端获取uId）
     * @param msg
     * @return
     * @since 1.0.0
     * @date 2020-11-10
     */
	public void insertAndSetMessage(Message msg) {
		if(msg == null || msg.getBody() == null) {
			return;
		}
		int times = msg.getBody().length()/MAX_VALUE;
        if (times > 1) {
	        int y = msg.getBody().length() % MAX_VALUE;
	        if(y != 0) {
	        	times ++;
	        }
	        String nextId = UUID.randomUUID().toString();
	        String curId = UUID.randomUUID().toString();
	        String body = msg.getBody();
	        msg.setBody(TO_EXT + "|" + curId);
	        LOGGER.debug("==== It needs to be split {} times ====", times);
	        for(int i = 0; i < times; i ++) {
	        	String ext = body.substring(i * MAX_VALUE, Math.min((i+1)*MAX_VALUE, body.length()));
	        	LOGGER.debug("==== the {} of splited ext is {} ====",i + 1, ext);
	        	Ext ext = createImsExt(nextId,ext,curId);
	        	extMapper.insert(ext);
	        	curId = nextId;
	        	nextId = i == times -2 ? null : UUID.randomUUID().toString();
	        }
        } 
	}
	
	public void queryAndSetMessage(Message msg) {
		if(msg == null || msg.getBody() == null) {
			return;
		}
		String[] ext = msg.getBody().split("\\|");
		if(TO_EXT.equals(ext[0])) {
			StringBuilder sb = new StringBuilder();
			String id = ext[1];
			while(id != null) {
				Ext ext = extMapper.selectByPrimaryKey(id);
				sb.append(ext.getExt());
				id = ext.getNextId();
			}
			LOGGER.debug("==== the whole body is {} ====", sb);
			msg.setBody(sb.toString());
		}
	
	}
	
	/**
	 * 创建实体类{@link ImsExt}
	 * @param nextId
	 * @param ext
	 * @param curId
	 * @return
	 * @since 1.0.0
	 * @date 2020-11-10
	 */
	private Ext createImsExt(String nextId, String ext, String curId) {
		Ext imsExt = new Ext();
		ext.setId(curId);
		ext.setNextId(nextId);
		ext.setExt(ext);
		ext.setBelong("IMS_MESSAGE|body");
		return imsExt;
	}

}
```

### PS：如何确定MAX_VALUE

对于Oracle来说，varchar2的最大长度是4000bytes，我们要想确定每一列到底能存多少字符串，有两种方法:

1. 通过Oracle的编码方式来确定

   ```sql
   select userenv(‘language’) from dual
   ```

   当查到具体的编码方式后，再进行对应字符串的切割，不过这种方式较为繁琐，而且不精确。

2. 直接在Oracle中存入字节

   ```java
   byte[] bytes = msg.getBody().getBytes();
   for(int i = 0; i < times; i ++) {
       byt[] subBytes = new byte[4000];
       System.copy(subBytes, bytes, i, i + 4000);
   	extMapper.insert(create(subBytes));
   }
   ```

   这个方法有一个弊端，就是需要我们在Ext这个JavaBean中把ext属性的类型改为byte[]