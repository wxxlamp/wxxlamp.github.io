---
title: "程序员如何配置MBP"
date: 2025-08-15 12:05
tags:
   - MacOS
   - 开发工具
   - 系统管理
   - 环境配置
categories:
   - 技术分享
description: "详细介绍MacOS系统目录结构及作为开发工具的最佳实践，涵盖常用命令、环境配置和系统管理技巧，帮助开发者更好地使用Mac进行开发工作。"
---

一转眼在公司四周年了，公司给我换了一个mbp14作为新的主子。

因为四年前刚接触Mac，所以不管安装什么都是下一步，导致有时候会发生莫名其妙的环境问题，什么mvn命令找不到，python版本不一致等等。正好趁着mbp13正式退役，抽时间了解下MAC系统。

同时，自己也不清楚安装的各种数据究竟存储在哪里。所以，借用这个机会，系统性的整理和学习下MacOS的基本概念和操作。

使用姿势可以直接看第二部分

# Mac的目录结构
类unix系统，不用像windows一样进行磁盘分区，所以我们也不用担心C盘垃圾数据太多影响操作系统的运行。在MAC中下载数据的时候，我们也不用考虑究竟要下载到哪个磁盘，这无疑降低了我们的决策成本。但是作为新手，还是要先粗略的了解下MAC的目录结构。

## 1.1 系统目录
系统目录在平时的使用中几乎接触不到，常见的可能有以下几个：

`/Applications`一些所有用户共享的app会安装在本目录下（使用homebrew会默认安装应用到该系统）

下面的表格中是一些系统目录常见的功能，其中前四个是与日常开发和使用相关的，其他的关系不大。

| **目录名** | **主要功能** | **特点** | **权限要求** | **常见用法** |
| --- | --- | --- | --- | --- |
| /Applications | 系统级应用程序 | 所有用户共享 | 需要管理员权限 | 安装供所有用户使用的应用 |
| /bin | 基本系统命令 | 核心可执行文件 | 系统级保护 | ls, cp, mv等基础命令 |
| /Volumes | 挂载点 | 外部设备挂载 | 系统管理 | USB、网络驱动器访问点 |
| /opt | 第三方软件包 | 可选软件安装 | 需要管理员权限 | Homebrew等包管理器使用 |
| /System | macOS核心系统文件 | 系统保护，只读 | 系统级保护 | ⚠️ 不要修改，系统运行必需 |
| /Library | 系统级库和配置 | 系统共享资源 | 需要管理员权限 | 系统框架、插件、字体等 |
| /Users | 所有用户主目录 | 包含所有用户文件夹 | 系统管理 | 用户数据存储根目录 |
| /sbin | 系统管理命令 | 管理员专用命令 | 需要root权限 | 系统维护和配置工具 |
| /usr | 用户程序和库 | 用户级系统程序 | 部分需要管理员权限 | 编程工具、库文件 |
| /etc | 系统配置文件 | 全局配置 | 需要管理员权限 | 系统服务配置、网络设置 |
| /var | 可变数据文件 | 动态变化的文件 | 混合权限 | 日志文件、缓存、邮件队列 |
| /tmp | 临时文件 | 重启后清除 | 所有用户可写 | 临时数据存储 |
| /dev | 设备文件 | 硬件设备接口 | 系统管理 | 硬件设备访问接口 |
| /private | 私有系统文件 | 系统内部文件 | 系统级保护 | ⚠️ 系统内部使用，勿修改 |
| /home | 用户目录符号链接 | 指向/Users | 系统管理 | 兼容Unix系统的用户目录 |
| /cores | 核心转储文件 | 程序崩溃信息 | 系统生成 | 调试崩溃程序使用 |


## 1.2 用户目录
日常的工作区基本都在 `/Users/$user/`目录下。所以我们日常数据的读写基本都在该目录下面。和windows系统一样，Mac推荐了一些常见的使用目录，供我们存放数据：

| **目录名** | **主要功能** | **特点** | **推荐用法** |
| --- | --- | --- | --- |
| ~/Applications | 用户个人应用 | 仅当前用户可用 | ✅ **安装个人应用的最佳位置** |
| ~/Documents | 个人文档 | 用户主要工作区 | ✅ **存储个人文档、项目文件、代码** |
| ~/Downloads | 下载文件 | 浏览器默认下载位置 | ✅ **下载文件的默认存储位置** |
| ~/Desktop | 桌面文件 | 桌面显示的文件 | 桌面快捷方式、临时文件 |
| ~/Library | 用户配置和数据 | 应用程序配置 | ✅ **开发者配置文件存储位置** |
| ~/Pictures | 图片和照片 | 媒体文件管理 | 个人照片、截图、图片素材 |
| ~/Movies | 视频文件 | 视频媒体库 | 个人视频收藏 |
| ~/Music | 音乐文件 | 音频媒体库 | 音乐库、音频文件 |


## 1.3 常用配置文件
除了常见的目录外，用户根目录还有一些很重要的配置文件，这些文件会在终端session更新的时候加载，我们常见的非系统命令（如java、mvn、node）等都是通过这些文件在session初始化时更细的。

其中在Mac Catalina之前，使用的是.bash_profile和.bashrc，现在这两个文件只作为兼容保留，推荐在Mac Catalina之后使用.zprofile和.zshrc。他们有什么作用呢？

当我们打开terminal.app时，系统会默认执行一遍.bash_profile和.zprofile里面的脚本

具体的执行顺序如下：

`login → /etc/zshenv → ~/.zshenv → /etc/zprofile → ~/.zprofile → /etc/zshrc → ~/.zshrc → /etc/zlogin → ~/.zlogin`

总的来说，第一次打开时，执行.zprofile，以后新开窗口（如在vscode中打开terminal）时执行.zshrc。所以推荐将全局变量和PATH写到.zprofile中，将函数、alias写到.zshrc中。注意，不建议把PATH或者JAVA_HOME写到.zprofile中，这样有可能会导致PATH路径重复且特别长，影响which查找效率。同时，GUI程序也会默认读取.zprofile的配置

具体的分类如下：

| **文件名** | **Shell类型** | **加载时机** | **主要用途** | **当前状态** |
| --- | --- | --- | --- | --- |
| **.zprofile** | Zsh | 登录时加载一次 | 登录初始化、GUI读取 | 🟢 推荐使用 |
| **.zshrc** | Zsh | 每次新终端会话 | Zsh交互式会话配置 | 🟢主要配置文件 |
| **.bash_profile** | Bash | 登录时加载一次 | Bash shell环境配置 | 🟡 兼容性保留 |


如果我们希望脚本的配置生效，只需要执行下面的命令即可：

```bash
source ~/.zshrc
```

## 1.4 隐秘的文件夹
在MAC的用户根目录中，有很多配置文件夹，以`.xx`开头，他们一般是存储各种程序（pyenv,git,nvm,vscode等）的基础配置，如下：

![Mac隐秘文件夹结构](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/b7b51d7e_mac_folders.png)

# 如何下载常用的工具
Mac的下载工具方式大体和windows一样，都包含app store和通过浏览器下载安装包两种方式。但是除此之外，Mac作为类unix系统，还是有一些更“高效”的下载方式

## 常用的下载工具
把mac作为开发工具，一定会下载很多没有GUI的程序，这种情况下，就不推荐用浏览器下载了。一般可以通过homebrew和curl下载。比较推荐homebrew，他是Mac专门用来管理软件包的工具，我们可以通过这个工具对常见的软件进行包管理、安装、删除、升级等，避免自己将来在删除程序的时候有删除不干净的情况。但是，请注意，homebrew无法安装同一软件的多个版本。譬如电脑上既存在python2和python3，这借助homebrew的能力是实现不了的，可以通过pyenv等专用工具实现，这个下文会讲到

| **使用场景** | **推荐工具** | **原因** | **存储目录** |
| --- | --- | --- | --- |
| 日常文件下载 | Safari/Chrome | 简单易用，安全可靠 | ~/Downloads/和~/Library/Application Support/Google/Chrome和~/Applications/Chrome Apps/ |
| 批量/自动化下载 | curl | 脚本化，可定制 | 通过`-o`制定目录 |
| UI软件安装 | App Store | 官方集成 | ~/Library/Application Support/App Store/和~/Applications/ |
| 命令行工具下载 | Homebrew | 包统一管理，类似于apt,pyenv,nvm | /opt/homebrew/ |


## 常见的homebrew命令
先列举下homebrew的常见命令：

```bash
# 查看Homebrew安装路径
brew --prefix

# 查看某个包的安装位置
brew --prefix <package-name>

# 清理缓存
brew cleanup

# 查看Homebrew占用空间
du -sh $(brew --prefix)

#删除缓存文件
rm -rf "$(brew --cache)"

#重新安装损坏的软件
brew reinstall git

# 查看安装的软件及版本
brew list --versions

#每日维护例程
brew update && brew upgrade && brew cleanup

#搜索并安装软件
brew search python
brew info python@3.11
brew install python@3.11

# 服务管理
brew install mysql
brew services start mysql
brew services list
```

如果使用homebrew的话，要注意设置国内的镜像。

# 常用的Mac App
这里列举下常用的app以及他们的安装方式

## 日常
| 应用名称 | 作用 | 安装方式 | 备注 |
| --- | --- | --- | --- |
| Chrome | 浏览器/主 | brew、浏览器、appStore | 主浏览器使用 |
| Firefox | 浏览器/备 | brew、浏览器、appStore | 特殊情况双开浏览器 |
| 搜狗输入法 | 习惯了 | brew、浏览器、appStore | 记忆比mac自带好，但是要小心泄露 |
| 微信 | 通讯 | brew、浏览器、appStore | Mac可以双开 |
| maccy | 剪切板 | brew、github | 存储近50条粘贴的记录 |
| Scroll Reverser | 鼠标翻转 | [浏览器](https://scroll-reverser.macupdate.com/) | 外接鼠标的滚轮方向和windows一致 |


## 效率工具
| 应用名称 | 作用 | 安装方式 | 备注 |
| --- | --- | --- | --- |
| Item2 | 终端 | brew、浏览器 | 比Mac自带的Terminal好用 |
| ohmyzsh | zsh自定义 | [github](https://github.com/ohmyzsh/ohmyzsh) | 更换主题，安装高亮、自动补全、快捷跳转目录 |
| Idea | Java开发 | 浏览器、Jetbrain Toolbox | Jetbrains Jvm系开发全家桶（rainbow插件） |
| Pycharm | Pyhon开发 | 浏览器、Jetbrain Toolbox | Jetbrains Python开发全家桶 |
| WebStorm | Js开发 | 浏览器、Jetbrain Toolbox | Jetbrains Web开发全家桶 |
| vscode | 编辑文本 | brew、浏览器 | python、Js开发（命令行直接code xx唤醒超方便） |
| light proxy | 代理工具 | github | 开发流量监控 |
| [clashX](https://github.com/bannedbook/ClashX) |  | [github](https://github.com/bannedbook/ClashX) | 代理 |
| Docker | 虚拟化 | brew | cask和命令行都可以 |


对于ohmyzsh来说，需要安装一些插件才可以更好的使用：

> 更换[spaceship主题](https://github.com/spaceship-prompt/spaceship-prompt)，安装[zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting/tree/master)插件，高亮显示命令等；安装[zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions)插件，历史命令自动补全；安装[autojump](https://github.com/wting/autojump)插件，快捷跳转目录
>

## 开发环境
### git支持多仓库
1. 通过ssh工具，生成两个git秘钥和公钥，将生成后的公钥复制到对应的多个仓库设置中

```shell
ssh-keygen -t rsa -b 4096 -C "wxxlamp@foxmail.com" -f ~/.ssh/id_rsa_person
ssh-keygen -t rsa -b 4096 -C "wxxlamp@work.com" -f ~/.ssh/id_rsa_work
```

2. 同时将这两个密钥分别配置在gitlab仓库和github后台上，然后配置.ssh/config如下

```bash
# GitHub
Host github.com
    HostName github.com
    User wxx

# 对应工作仓库
Host gitlab.work.com
    HostName gitlab.work.com
    User work
    IdentityFile ~/.ssh/id_rsa_work
```

3. 使用`ssh -T@github.com`进行联通性测试

### Java&Maven Runtime
因为homebrew不支持单app多版本，所以像Java、Python、Node等环境需要特殊的工具配置。

对于Jvm系来说，可以使用sdkman全局管理不同版本的Java和maven配置：

```bash
# 1. 安装 SDKMAN
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# 2. 查询并安装 Java 21
sdk list java
sdk install java 21.0.4-tem

# 3. 设为默认
sdk default java 21.0.4-tem

# 4. 安装 Maven 最新版
sdk install maven

# 5. 查看结果
sdk current
```

常见的sdkman命令

| 命令 | 作用 | 示例 / 备注 |
| --- | --- | --- |
| **查看所有可装 candidate** | 列出支持的语言/工具 | `sdk list` |
| **查看某个 candidate 的所有版本** | 例如 java | `sdk list java` |
| **安装指定版本** | 安装 openjdk 17 | `sdk install java 17.0.12` |
| **安装并使用最新稳定版** | 省略版本号即可 | `sdk install maven` |
| **切换到已安装的某个版本** | 仅对当前 shell 生效 | `sdk use java 21.0.4-tem` |
| **设置默认版本** | 全局生效（写入 ~/.sdkmanrc） | `sdk default java 21.0.4-tem` |
| **查看当前正在使用的版本** | 列出所有 candidate 的当前版本 | `sdk current` |
| **查看单个 candidate 当前版本** | 只看 java | `sdk current java` |
| **卸载某个版本** | 彻底删除本地副本 | `sdk uninstall java 11.0.25` |
| **查看环境变量路径** | 调试/脚本中常用 | `sdk home java 17.0.12-tem` |


### Python runtime
python市面上的管理器是在太多了。同时，要注意，MAC出厂就会自带python运行时，在`/usr/bin/python3`目录下。所以如果不是开发python项目，使用Mac自带即可。但是很多程序对python的版本都有要求，所以我们要通过第三方工具来完成python版本的切换和包管理。令人遗憾的是，许多其他的python版本和包管理工具，对于初学者来说，不眼花缭乱是不可能的，如下所示：

| **工具** | **核心作用** | **管理范围** | **典型场景** |
| :--- | :--- | :--- | :--- |
| venv | 轻量级虚拟环境管理 | 仅虚拟环境（依赖隔离） | 简单项目，依赖 Python 3.3 + 内置功能 |
| virtualenv | 增强版虚拟环境管理 | 仅虚拟环境（依赖隔离） | 多项目依赖隔离，支持 Python 2/3 |
| pyenv | Python 版本管理 | 仅 Python 解释器版本 | 多版本 Python 共存切换 |
| conda | 环境管理（不止 Python） | 版本管理 + 虚拟环境 + 包管理 | 数据科学、跨语言项目 |


一句话解释，pyenv是用来切换python版本的，virtualenv是提供虚拟环境，各个环境下载的python依赖相互隔离。conda是virtualenv的增强版，可以管理除了python以外其他科学计算的包

推荐：使用pyenv做全局的python版本管理，同时使用pyenv-virtualenv做python的虚拟环境管理。除此之外，把conda作为pyenv的一个虚拟环境，如果项目需要使用非python包，则通过pyenv切换到conda环境。

> 这里可以稍微聊下几种工具提供虚拟环境的机制。
>
> 对于pyenv来说，首先要保证python的PATH指向pyenv，如果设置global的python版本，本质是在`~/.pyenv/version`文件中设置python版本。如果是设置local的python版本，说明只在当前文件夹生效，本质是在文件夹的根目录创建一个`.python-version`的文件，里面记录了python的版本
>
> 对于virtualenv来说，当我们激活当前虚拟环境，他会在当前目录新建一个venv目录，该目录会存储当前虚拟环境的所有依赖（python版本仍然使用的pyenv指定的版本，不会新copy一份）。如果关闭shell，下次打开需要重新激活环境
>
> 对于conda来说，当我们激活当前虚拟环境，他会在conda安装目录新建一个虚拟环境目录，并且会copy一份python版本，同时后续的所有依赖也会存储在该目录。如果关闭shell，下次打开需要重新激活环境
>

常见命令行如下

```shell
# 确认当前python的路径
which python3

#======= pyenv command
# List all installed Python versions in pyenv
pyenv versions

# Install a specific Python version (if not already installed):
pyenv install 3.11.4

# set the python system or current versions
pyenv global 3.11.4  

cd /path/to/your/project
pyenv local 3.10.8  # Creates a .python-version file in the project

#======= conda command
# 通过pyenv管理conda环境
pyenv install miniconda3-latest

# shell级别切换python版本
pyenv shell miniconda3-latest

# List all conda environments:
conda env list

# Create a new environment with a specific Python version
conda create --name myenv python=3.9 

# Activate an environment 
conda activate myenv
```

```shell
# 查看当前pip安装的依赖地址
pip show pip | grep Location
```

### Node runtime
可以使用nvm进行管理node的版本。nvm推荐直接使用curl下载

```shell
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
nvm install --lts     # 安装最新的 LTS 版本
nvm install 20.12.2   # 安装指定版本
nvm use 20.12.2       # 切换到指定版本
nvm current
nvm list
```



