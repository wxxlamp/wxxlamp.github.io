---
title: A MacBook Pro Setup Guide for Developers
date: 2025-08-15 12:05
tags:
  - 开发工具
  - 计算机系统
categories:
  - 基础夯实
description: >-
  A detailed guide to the macOS directory structure and development best
  practices, including common commands, environment setup, runtime version
  management, and system administration tips.
lang: en
translation_of: how-to-use-mac
---

In the blink of an eye, I had been at the company for four years, and it replaced my old machine with a 14-inch MacBook Pro as my new master.

When I first encountered a Mac four years ago, I installed everything by clicking Next. That occasionally produced baffling environment problems: `mvn` could not be found, Python versions differed, and so on. With the old 13-inch MBP officially retiring, this was a good opportunity to understand macOS properly.

I also did not know where the data from all those installations was stored. I therefore used the opportunity to organize and study basic macOS concepts and operations systematically.

Readers interested only in practical setup can jump directly to the second part.

# The Mac Directory Structure

Unix-like systems do not require Windows-style disk partitions, so there is no concern that excessive junk on drive C will impair the OS. When downloading on a Mac, we need not decide which disk should hold the file, reducing decision cost. Beginners should nevertheless understand the directory structure roughly.

## 1.1 System Directories

Ordinary use rarely touches system directories. Common examples include:

`/Applications`, where applications shared by all users are installed. Homebrew installs applications there by default.

The following table lists common system directories. The first four are most relevant to daily development and use.

| **Directory** | **Main purpose** | **Characteristics** | **Permissions** | **Common use** |
| --- | --- | --- | --- | --- |
| /Applications | System-wide applications | Shared by all users | Administrator required | Applications for every user |
| /bin | Basic system commands | Core executables | System protected | Basic commands such as ls, cp, mv |
| /Volumes | Mount points | External devices | System managed | USB and network-drive access |
| /opt | Third-party packages | Optional software | Administrator required | Package managers such as Homebrew |
| /System | Core macOS files | Protected and read-only | System protected | ⚠️ Required by the OS; do not modify |
| /Library | System-wide libraries and configuration | Shared resources | Administrator required | Frameworks, plugins, fonts |
| /Users | User home directories | Contains every user's folder | System managed | Root of user-data storage |
| /sbin | Administration commands | Administrator utilities | Root required | System maintenance and configuration |
| /usr | User programs and libraries | User-level system programs | Some actions require administrator | Programming tools and libraries |
| /etc | System configuration | Global configuration | Administrator required | Services and network settings |
| /var | Variable data | Dynamically changing files | Mixed permissions | Logs, caches, mail queues |
| /tmp | Temporary files | Cleared after restart | Writable by all users | Temporary storage |
| /dev | Device files | Hardware interfaces | System managed | Hardware-device access |
| /private | Private system files | Internal files | System protected | ⚠️ Internal use; do not modify |
| /home | User-directory symbolic link | Points to /Users | System managed | Unix compatibility |
| /cores | Core dumps | Crash information | System generated | Debugging crashed programs |

## 1.2 User Directories

Daily work happens mainly under `/Users/$user/`, so most ordinary reads and writes occur there. Like Windows, macOS recommends standard locations for user data:

| **Directory** | **Main purpose** | **Characteristics** | **Recommended use** |
| --- | --- | --- | --- |
| ~/Applications | Personal applications | Current user only | ✅ **Best location for personal applications** |
| ~/Documents | Personal documents | Main workspace | ✅ **Documents, projects, and code** |
| ~/Downloads | Downloads | Browser default | ✅ **Default downloaded-file location** |
| ~/Desktop | Desktop files | Visible on desktop | Shortcuts and temporary files |
| ~/Library | User configuration and data | Application configuration | ✅ **Developer configuration files** |
| ~/Pictures | Images and photographs | Media management | Photos, screenshots, image assets |
| ~/Movies | Video files | Video library | Personal videos |
| ~/Music | Audio files | Music library | Music and audio |

## 1.3 Common Configuration Files

The user home also contains important configuration files loaded when terminal sessions initialize. Nonsystem commands such as Java, Maven, and Node are commonly added to the environment through these files.

Before macOS Catalina, Bash used `.bash_profile` and `.bashrc`. They remain for compatibility, while Catalina and later recommend `.zprofile` and `.zshrc` for Zsh.

When `Terminal.app` opens, the system executes the login profile scripts. The detailed sequence is:

`login → /etc/zshenv → ~/.zshenv → /etc/zprofile → ~/.zprofile → /etc/zshrc → ~/.zshrc → /etc/zlogin → ~/.zlogin`

Broadly, `.zprofile` runs at login, while `.zshrc` runs for each new interactive terminal, including one opened inside VS Code. Put login initialization in `.zprofile`, and functions and aliases in `.zshrc`. Avoid repeatedly appending `PATH` or `JAVA_HOME` there in ways that produce a duplicated, extremely long path and slow `which`. GUI applications may also read `.zprofile`.

| **File** | **Shell** | **When loaded** | **Main purpose** | **Status** |
| --- | --- | --- | --- | --- |
| **.zprofile** | Zsh | Once at login | Login initialization and GUI environment | 🟢 Recommended |
| **.zshrc** | Zsh | Every new terminal session | Interactive Zsh configuration | 🟢 Main configuration file |
| **.bash_profile** | Bash | Once at login | Bash environment configuration | 🟡 Retained for compatibility |

To apply updated shell configuration, run:

```bash
source ~/.zshrc
```

## 1.4 Hidden Folders

The Mac user home contains many configuration folders beginning with `.`, generally storing settings for programs such as pyenv, Git, nvm, and VS Code:

![Mac hidden-folder structure](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/b7b51d7e_mac_folders.png)

# Downloading Common Tools

As on Windows, Mac software can be installed through the App Store or packages downloaded in a browser. As a Unix-like system, macOS also offers more efficient methods.

## Common Download Tools

A development Mac needs many programs without GUIs, for which browser downloads are inconvenient. Homebrew and `curl` are common choices. I recommend Homebrew, a Mac package manager that installs, removes, and upgrades software consistently and avoids incomplete later removal. Note that Homebrew is not designed to manage several versions of one tool simultaneously. For Python 2 and Python 3 side by side, use a specialized version manager such as pyenv, discussed below.

| **Scenario** | **Recommended tool** | **Reason** | **Storage location** |
| --- | --- | --- | --- |
| Ordinary downloads | Safari/Chrome | Simple, safe, reliable | ~/Downloads/, Chrome application-support and app folders |
| Batch or automated downloads | curl | Scriptable and customizable | Chosen with `-o` |
| GUI installation | App Store | Official integration | App Store support and ~/Applications |
| Command-line tools | Homebrew | Unified package management like apt | /opt/homebrew/ |

## Common Homebrew Commands

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

When using Homebrew in mainland China, configure a domestic mirror.

# Common Mac Applications

Here are useful applications and ways to install them.

## Daily Use

| Application | Purpose | Installation | Notes |
| --- | --- | --- | --- |
| Chrome | Primary browser | brew, browser, App Store | Main browser |
| Firefox | Backup browser | brew, browser, App Store | A second browser for special cases |
| Sogou Input | Familiar input method | brew, browser, App Store | Better memory than Apple's, but consider privacy |
| WeChat | Communication | brew, browser, App Store | Two instances can run on Mac |
| Maccy | Clipboard | brew, GitHub | Keeps roughly fifty clipboard entries |
| Scroll Reverser | Mouse scrolling | [Browser](https://scroll-reverser.macupdate.com/) | Makes an external mouse scroll like Windows |

## Productivity Tools

| Application | Purpose | Installation | Notes |
| --- | --- | --- | --- |
| iTerm2 | Terminal | brew, browser | More capable than Terminal.app |
| Oh My Zsh | Zsh customization | [GitHub](https://github.com/ohmyzsh/ohmyzsh) | Themes, highlighting, completion, fast directory jumps |
| IntelliJ IDEA | Java development | Browser, JetBrains Toolbox | JetBrains JVM suite; Rainbow plugin |
| PyCharm | Python development | Browser, JetBrains Toolbox | JetBrains Python IDE |
| WebStorm | JavaScript development | Browser, JetBrains Toolbox | JetBrains web IDE |
| VS Code | Text editing | brew, browser | Python/JS; convenient `code xx` command |
| LightProxy | Proxy tool | GitHub | Development traffic monitoring |
| [ClashX](https://github.com/bannedbook/ClashX) | Proxy | [GitHub](https://github.com/bannedbook/ClashX) | Network proxy |
| Docker | Virtualization | brew | Both cask and CLI are available |

Oh My Zsh is best used with several plugins:

> Switch to the [Spaceship theme](https://github.com/spaceship-prompt/spaceship-prompt); install [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting/tree/master) to highlight commands; install [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions) for history completion; and install [autojump](https://github.com/wting/autojump) for fast directory navigation.
>

## Development Environment

### Git with Multiple Repositories

1. Use SSH tools to generate two private/public key pairs and copy the public keys into the corresponding repository settings.

```shell
ssh-keygen -t rsa -b 4096 -C "wxxlamp@foxmail.com" -f ~/.ssh/id_rsa_person
ssh-keygen -t rsa -b 4096 -C "wxxlamp@work.com" -f ~/.ssh/id_rsa_work
```

2. Configure the keys in GitHub and the GitLab repository, then configure `.ssh/config`:

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

3. Test connectivity with `ssh -T@github.com`.

### Java and Maven Runtimes

Because Homebrew does not manage multiple versions of one application conveniently, Java, Python, and Node need specialized tools.

For the JVM ecosystem, SDKMAN can manage Java and Maven versions globally:

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

Common SDKMAN commands:

| Command | Purpose | Example or note |
| --- | --- | --- |
| **List candidates** | Supported languages and tools | `sdk list` |
| **List versions** | Versions of one candidate | `sdk list java` |
| **Install a version** | Install OpenJDK 17 | `sdk install java 17.0.12` |
| **Install latest stable** | Omit the version | `sdk install maven` |
| **Use an installed version** | Current shell only | `sdk use java 21.0.4-tem` |
| **Set default version** | Global default | `sdk default java 21.0.4-tem` |
| **Show current versions** | All candidates | `sdk current` |
| **Show one current version** | Java only | `sdk current java` |
| **Uninstall a version** | Remove local copy | `sdk uninstall java 11.0.25` |
| **Show installation path** | Useful in scripts | `sdk home java 17.0.12-tem` |

### Python Runtime

Python has an overwhelming number of managers. macOS also ships a Python runtime at `/usr/bin/python3`, which is sufficient if you are not developing Python projects. Many programs require particular Python versions, however, so third-party tools manage versions and packages.

| **Tool** | **Core purpose** | **Scope** | **Typical use** |
| :--- | :--- | :--- | :--- |
| venv | Lightweight virtual environments | Dependency isolation only | Simple projects; built into Python 3.3+ |
| virtualenv | Enhanced virtual environments | Dependency isolation only | Multiple projects; Python 2/3 |
| pyenv | Python version management | Interpreter versions only | Several Python versions side by side |
| conda | Environment management beyond Python | Versions, environments, packages | Data science and cross-language projects |

Put simply, pyenv switches Python versions, virtualenv provides isolated dependency environments, and conda extends environment management to non-Python scientific packages.

I recommend pyenv for global Python versions and pyenv-virtualenv for virtual environments. Conda can itself be installed as a pyenv-managed environment; switch to it when a project requires non-Python packages.

> These tools implement environments differently.
>
> Pyenv first ensures that `PATH` points to pyenv. Setting a global version writes it to `~/.pyenv/version`. Setting a local version applies only inside one folder by creating `.python-version` at the project root.
>
> Activating virtualenv creates a `venv` directory that stores the environment's dependencies. It uses the Python version selected by pyenv rather than copying another interpreter. A new shell must reactivate the environment.
>
> Activating conda creates an environment directory beneath the conda installation, copies a Python interpreter there, and stores later dependencies in that directory. A new shell must reactivate it.
>

Common commands:

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

### Node Runtime

Use nvm to manage Node versions. Installing nvm directly with `curl` is recommended.

```shell
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
nvm install --lts     # 安装最新的 LTS 版本
nvm install 20.12.2   # 安装指定版本
nvm use 20.12.2       # 切换到指定版本
nvm current
nvm list
```


