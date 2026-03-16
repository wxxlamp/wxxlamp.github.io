---
title: "Hexo使用指南"
date: 2020-12-16 19:53
tags:
   - Hexo
categories:
   - 采坑记录
description: "Hexo博客从零搭建实战指南，涵盖环境准备、安装配置、GitHub Pages部署及主题更换，收录常见坑点及解决方案。"
---

最近用了hexo搭建博客，踩了许多坑，所以想总结一篇文章。包括每一步的做法，以及可能踩的坑，以及应对的办法

大家可以参考这个文档；[easyhexo](https://easyhexo.com/1-Hexo-install-and-config/1-3-config-hexo.html#%E9%85%8D%E7%BD%AE-hexo-2)

<!--more-->

### 1. 环境准备
在使用HEXO之前，我们需要安装node.js和npm（因为node.js已经包含了npm，所以我们只需要更新npm即可）。同时因为npm是国外的源，我们一般都会设置淘宝的镜像，或者是用cnpm

[下载node.js和npm](https://www.cnblogs.com/jianguo221/p/11487532.html)，我是按照这个教程来的，其中的安装vue我们可以不用搞。

### 2. 下载HEXO

之后我们就需要下载hexo了。这个比较简单，用到下面这三个命令就可以了
```js
    npm install hexo-cli // 下载hexo
    hexo -v // 查看是否安装成功
    hexo init // 初始化hexo文件夹
    npm install // 下载模块依赖
```
也可以看这个链接：[安装hexo](https://www.jianshu.com/p/343934573342)

#### 可能出现的问题
1. ejs安装失败，具体信息如下：
    ```js
    npm ERR! code ELIFECYCLE
    npm ERR! errno 1
    npm ERR! ejs@2.7.4 postinstall: `node scripts/build.js`
    npm ERR! Exit status 1
    npm ERR!
    npm ERR! Failed at the ejs@2.7.4 postinstall script.
    npm ERR! This is probably not a problem with npm. There is likely additional logging output above.
    ```
    这个大部分是网络原因，有两个解决办法，一个是换网，一个是使用如下命令
    
    `npm install ejs@2.7.4 --ignore-scripts`
    
    PS `--ignore-scripts`可以解决很多这样的问题。原理是这个命令可以略过我们指定的包，但是我现在还不清楚为什么略过以后，虽然不报错，但是我们的程序可以正常运行呢？
    
2. 产生fsevents warn
    ```js
    npm WARN optional SKIPPING OPTIONAL DEPENDENCY: fsevents@1.2.9 (node_modules\fsevents):

    npm WARN notsup SKIPPING OPTIONAL DEPENDENCY: Unsupported platform for fsevents@1.2.9: wanted {"os":"darwin","arch":"any"} (current: {"os":"win32","arch":"x64"})
    ```
    这是因为我们用的windows系统，而hexo默认会下载只在Mac上有用的fsevents包，所以会有这个warn，不用管即可





### 3. 配置HEXO

当我们安装完毕的时候，就需要对Hexo进行一些配置，具体是通过`_config.yml`文件来完成的

#### Hexo结构
```js
    .deploy_git 
    node_modules //包所需要的依赖
    public // 静态网页存储的目录
    scaffolds // 样本
    source // 我们自己的md文件
    themes // 主题文件
    .gitignore
    _config.yml // 配置
    db.json
    package.json
    package-lock.json
```

### 4. 发布hexo

[hexo的部署](https://zhuanlan.zhihu.com/p/60578464)
发布hexo有两种方式，一种是使用hexo d 命令，一种是直接将public目录下的所有文件git push到github或者gitee上

#### 可能出现的问题
部署之后没有css样式，这个有几种情况：
1. 静态文件，如图片，css等的地址不对
2. 网络延时
3. 本地正确但是远程不对，这种情况下，就需要我们使用git push的方式进行部署

还有一个问题就是在使用`hexo d`之后抛出`ERROR Deployer not found: git`,这是因为我们没有install与git匹配的工具

`npm install --save hexo-deployer-git`

### 5. 更换主题

更换主题可以通过[Themes](https://hexo.io/themes/)来进行选择

在hexo5.1版本之前，我们下载主题一般是通过`git clone`的方式把主题下载到theme包中，但是在5.1+的版本中，我们需要使用npm install 来下载主题 *如果你刚进行完hexo init的话就会发现，themes文件夹是空的，这是因为hexo的原主题也通过npm也在了*

#### 可能出现的问题
1. 在更换主题的过程中，因为使用的npm包不一样，所以也有可能出现下载包失败的问题，如
     ```js
    npm ERR! code ELIFECYCLE
    npm ERR! errno 1
    npm ERR! node-sass@4.13.1 postinstall: `node scripts/build.js`
    npm ERR! Exit status 1
    npm ERR!
    npm ERR! Failed at the node-sass@4.13.1 postinstall script.
    npm ERR! This is probably not a problem with npm. There is likely additional logging output above.
    ```
    这时，我们需要设置sass源，即
    ```js
    npm config set sass_binary_site=https://npm.taobao.org/mirrors/node-
    ```
2. 对于hexo5.1+来说，主题文件默认是用npm的方式而不是git的方式下载，这样就会导致如下的warn
    ```js
    ERROR {
      err: [Error: EISDIR: illegal operation on a directory, read] {
        errno: -4068,
        code: 'EISDIR',
        syscall: 'read'
      }
    } Plugin load failed: %s hexo-theme-landscape

    ```
    这个没啥大问题，继续弄就完事了
    
### 6. 常见命令汇总
#### npm
```js
    npm install // 根据当前目录下的package.json安装所需依赖
    npm config list // 列出当前npm的配置
    npm install -g // 全局安装包
    npm install -save //不仅会安装，而且会把模块依赖写入package.json中的dependencies 节点 
```

#### hexo

```
    hexo clean // 删除public文件的内容
    hexo g // 生成静态文件到public
    hexo s // 本地运行
    hexo d // 发布静态文件
```