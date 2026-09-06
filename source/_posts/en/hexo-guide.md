---
title: Building a Blog with Hexo and GitHub Pages
date: 2020-12-16 19:53
tags:
  - 博客与写作
  - 开发工具
categories:
  - 采坑记录
description: >-
  A hands-on guide to building a Hexo blog from scratch, covering environment
  setup, installation, configuration, GitHub Pages deployment, theme changes,
  and common pitfalls with their solutions.
lang: en
translation_of: hexo-guide
---

I recently used Hexo to build a blog and ran into many issues, so I want to summarize them in one article. It covers each step, the possible pitfalls, and how to handle them.

You can refer to this guide: [easyhexo (in Chinese)](https://easyhexo.com/1-Hexo-install-and-config/1-3-config-hexo.html#%E9%85%8D%E7%BD%AE-hexo-2)

<!--more-->

### 1. Environment Setup
Before using HEXO, we need to install node.js and npm (because node.js already includes npm, so we only need to update npm). At the same time, because npm uses a foreign registry, we usually set the Taobao mirror, or use cnpm

[Download node.js and npm (in Chinese)](https://www.cnblogs.com/jianguo221/p/11487532.html), I followed this tutorial, and we can skip the Vue installation part.

### 2. Download HEXO

Then we need to download Hexo. This is quite simple; the following three commands are enough
```js
    npm install hexo-cli // 下载hexo
    hexo -v // 查看是否安装成功
    hexo init // 初始化hexo文件夹
    npm install // 下载模块依赖
```
You can also read this link: [Installing Hexo (in Chinese)](https://www.jianshu.com/p/343934573342)

#### Possible Issues
1. EJS installation fails, with the detailed error shown below:
    ```js
    npm ERR! code ELIFECYCLE
    npm ERR! errno 1
    npm ERR! ejs@2.7.4 postinstall: `node scripts/build.js`
    npm ERR! Exit status 1
    npm ERR!
    npm ERR! Failed at the ejs@2.7.4 postinstall script.
    npm ERR! This is probably not a problem with npm. There is likely additional logging output above.
    ```
    This is mostly due to network issues. There are two solutions: switch networks, or use the following command

    `npm install ejs@2.7.4 --ignore-scripts`

    PS `--ignore-scripts` can solve many such problems. The principle is that this command can skip the package we specify, but I still do not fully understand why, after skipping it, the program can run normally even though no error is reported.
    
2. The `fsevents` warn appears
    ```js
    npm WARN optional SKIPPING OPTIONAL DEPENDENCY: fsevents@1.2.9 (node_modules\fsevents):

    npm WARN notsup SKIPPING OPTIONAL DEPENDENCY: Unsupported platform for fsevents@1.2.9: wanted {"os":"darwin","arch":"any"} (current: {"os":"win32","arch":"x64"})
    ```
    This happens because we are using Windows, while Hexo by default downloads the `fsevents` package, which is only useful on Mac, so this warning appears. We can safely ignore it





### 3. Configure HEXO

Once everything is installed, we need to configure Hexo through the `_config.yml` file

#### Hexo Structure
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

### 4. Publish Hexo

[Hexo deployment (in Chinese)](https://zhuanlan.zhihu.com/p/60578464)
There are two ways to publish Hexo: one is to use the `hexo d` command, and the other is to directly git push all files in the `public` directory to GitHub or Gitee

#### Possible Issues
After deployment, there is no CSS styling. This can happen for several reasons:
1. The paths to static files such as images and CSS are incorrect
2. Network latency
3. The local version is correct but the remote version is not. In this case, we need to deploy using `git push`

Another issue is that after running `hexo d`, it throws `ERROR Deployer not found: git`, because we have not installed the tool matched to git

`npm install --save hexo-deployer-git`

### 5. Change the Theme

You can choose a theme through [Themes](https://hexo.io/themes/)

Before Hexo 5.1, we usually downloaded themes into the theme folder with `git clone`. But in version 5.1+, we need to use `npm install` to download themes. *If you have just run `hexo init`, you will find that the `themes` folder is empty, because Hexo's default theme is also installed through npm.*

#### Possible Issues
1. During theme changes, because the npm packages are different, package downloads may also fail, for example:
     ```js
    npm ERR! code ELIFECYCLE
    npm ERR! errno 1
    npm ERR! node-sass@4.13.1 postinstall: `node scripts/build.js`
    npm ERR! Exit status 1
    npm ERR!
    npm ERR! Failed at the node-sass@4.13.1 postinstall script.
    npm ERR! This is probably not a problem with npm. There is likely additional logging output above.
    ```
    At this point, we need to set the sass source, namely
    ```js
    npm config set sass_binary_site=https://npm.taobao.org/mirrors/node-
    ```
2. For Hexo 5.1+, theme files are downloaded by default with npm instead of git, which leads to the following warn
    ```js
    ERROR {
      err: [Error: EISDIR: illegal operation on a directory, read] {
        errno: -4068,
        code: 'EISDIR',
        syscall: 'read'
      }
    } Plugin load failed: %s hexo-theme-landscape

    ```
    This is not a big problem. Just keep going
    
### 6. Common Commands Summary
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
