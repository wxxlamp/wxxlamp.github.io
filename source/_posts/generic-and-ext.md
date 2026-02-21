---
title: 泛型通配符和扩展字段
date: 2023-08-04
tags:
  - Java
categories:
  - 场景实践
---

# 1. 问题引出

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
public class QuotaInfoView {

    /***
     * 额外信息
     */
    private Map<String, Object> extra;

    public void addExtraMap(String key, Object value) {
        if (extra == null) {
            extra = new HashMap<>(16);
        }
        extra.put(key, value);
    }

    public void addExtraMap(Map<String, Object> map) {
        if (MapUtils.isEmpty(map)) {
            return;
        }
        if (extra == null) {
            extra = Maps.newHashMapWithExpectedSize(map.size());
        }
        extra.putAll(map);

    }
}

如果客户端想要使用如下方式调用的话，则会编译失败

1
2
3
4
public void test() {
	Map<String, String> map = new HashMap<>();
    quotaInfoView.addExtraMap(map); 
}

# 2. 巧用泛型通配符解决

那么对于以上的问题我们怎么解决呢？可以使用三种泛型方式来解决

## 尝试一

只要是String及其父类都可以放进来

1
2
3
4
5
6
7
8
9
10
public void addExtraMap(Map<String, ? super String> map) {
    if (MapUtils.isEmpty(map)) {
        return;
    }
    if (extra == null) {
        extra = Maps.newHashMapWithExpectedSize(map.size());
    }
    extra.putAll(map);

}

但是对于这种形式，如果我使用如下的写法，仍然会编译失败

1
2
3
4
public void test() {
	Map<String, Integer> map = new HashMap<>();
    quotaInfoView.addExtraMap(map); 
}

## 尝试二

我们看一下String和Integer的通用父类是谁，那一定是object了

1
2
3
4
5
6
7
8
9
10
public void addExtraMap(Map<String, ? extends Object> map) {
    if (MapUtils.isEmpty(map)) {
        return;
    }
    if (extra == null) {
        extra = Maps.newHashMapWithExpectedSize(map.size());
    }
    extra.putAll(map);

}

这种方式还可以再简化

1
2
3
4
5
6
7
8
9
10
public void addExtraMap(Map<String, ?> map) {
    if (MapUtils.isEmpty(map)) {
        return;
    }
    if (extra == null) {
        extra = Maps.newHashMapWithExpectedSize(map.size());
    }
    extra.putAll(map);

}

## 推荐阅读

[EffectiveJava]读书笔记

# 3. 扩展字段的推荐写法

大家都特别喜欢用扩展字段，但是开发没有银弹，扩展字段用时一时爽，维护火葬场，如下所示：
有两个问题，一个是类型强转抛出NPE等，一个是不知道扩展字段里面究竟放的什么

1
2
3
4
public void test() {
    // 如果a=null，则抛出npe
    long a = (long)model.getExt("a");
}

那么怎么才能在使用扩展字段的同时，也降低我们的维护成本呢？笔者推荐一种处理方式：

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
public class ExtendInfoKey<T> {

    /**
     * key
     */
    private final String key;

    /**
     * class
     */
    private final Class<T> clazz;

    public ExtendInfoKey(String key, Class<T> clazz) {
        this.key = key;
        this.clazz = clazz;
    }

    public String getKey() {
        return key;
    }

    public Class<T> getClazz() {
        return clazz;
    }
}

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
public class ExtendInfoUtils {

    public static <T> T getExtendValue(ExtendInfoKey<T> key, Map<String, String> attrs) {
        if (MapUtils.isEmpty(attrs)) {
            return null;
        }
        String value = attrs.get(key.getKey());
        return JSON.parseObject(value, key.getClazz());
    }

    public static <T> void addExtendInfo(ExtendInfoKey<T> key, T value, Map<String, String> attrs) {
        if (Objects.isNull(attrs)) {
            throw new NullPointerException("attrs can not be null");
        }
        if (value != null) {
            attrs.put(key.getKey(), JSON.toJSONString(value));
        }
    }
}
