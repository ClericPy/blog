---
title: "再谈 Python 的打包与发布"
date: 2021-05-07T22:10:51+08:00
description: "时隔一年, 再随便聊聊 Python 打包和发布遇到的那些事儿"
categories: Python
draft: false
---

> 时隔一年, 再随便聊聊 Python 打包和发布遇到的那些事儿

## 接上回

入职新公司之后遇到 Python 打包发布的问题, 由于基础建设以及技术选型等历史遗留问题, 只能使用 Python 写的工具, 所以基本告别 `pipenv` / `venv` / `poetry` 等常见的发布方式, 遇到需要第三方依赖的功能, 打包依赖变得非常费劲.

考虑过像 go 一样打包一些二进制文件, 但是性能和兼容性等方面特别不友好, 所以还是打算使用 `zipapp` 那种方式来搞. `pyinstaller / venv / pipenv / poetry / setuptools / shiv / PyOxidizer` 这些的使用体验, 其实本身还是不错的.

## 新的选择

目前这类比较成熟的几个打包用的库里面, `shiv` 算是生态还算健康的选择, 类似的 `pex` / `superzippy` 使用过程中有挺多缓存或者其他不方便的地方, 所以用了大概三个多月 `shiv` (https://github.com/linkedin/shiv), 期间挺多小问题能解决的都解决了, 不能解决的提 issue 作者也比较快地支持了.

然而最后还是选择自己开发个类似项目 `zipapps`, 因为下面几个原因 `shiv` 支持的不是很方便:

1. 不能在打包时候设置默认 `SHIV_ROOT` 默认推到 HOME 目录在某些场景缺少 HOME 会报错, 每次手动定义这个环境变量又感觉很冗余
   1. 提过 issue 以后目前支持上了
2. 每次重新打包以后要重新创建缓存, 时间久了导致系统磁盘浪费几 GB 空间, 其实这是最主要的那个原因
   1. 有别人提了 `build_id` 的建议, 貌似没通过
3. 每次需要解压**全部**内容做缓存
   1. 实际上 `zipapp` 借助 `zipimport` 自带能力, 有的库是不需要解压的, 这样可以保证发布时的 `standalone` 特性
4. 跨平台和跨 Python 版本能力比较薄弱
   1. 比如 Python3.7 打包的依赖里有 C 编译的库, 这就没法给 Python 3.8 使用, 再比如 Windows 上打包的代码, 到了 Linux 上也有可能有兼容问题
5. 有时候需要合并多个 `pyz` 文件里的依赖一起使用, 就像是添加了多个 `sys.path`
   1. 比如: 有一个包含 bottle 的 `bottle.pyz`, 还有包含 requests 的 `requests.pyz`, 二者组合使用

## 使用 `Zipapps`

### 简单的使用

#### 安装

>  python3 -m pip install -U zipapps

#### 场景 1

> 需要打包发布 Linux 打包机上的工具

1. 假设有一个爬虫脚本, 依赖了第三方库 `requests`
2. `python -m zipapps -c -a entrypoint.py -m entrypoint:main -o crawler.py requests`
3. 现在当前目录得到一个后缀名是 `py` 的 zip 文件 `crawler.py`
   1. 这里使用 `py` 做后缀名, 是因为有的系统可以直接双击运行, 否则以 `zip` 结尾更准确, 以 `pyz` 结尾更富含语义
4. 通过 `python3 crawler.py` 执行即可完成任务

特殊情况:

1. 如果依赖的除了 `requests`, 还有 `psutil` 这类包含 `.so` / `.pyd` 的 C 编译的库, 则需要添加以下参数保证执行的时候将它们缓存到本地, 否则无法正确导入
   1. `-u="*"` 可以在运行时解压所有文件, 如果只希望解压最小数量, 可以使用 `-u="AUTO"` 替代
   2. 默认不指定 `-up` 参数的时候, 会在当前目录下解压: `./zipapps_cache/crawler`
2. 如果不希望执行的时候输入 `python3` , 可以通过以下参数指定默认解释器路径, 然后使用 `./crawler.py` 直接运行
   1. `-p /usr/bin/python3`  会将参数的内容放入首行 `shebang`
   2. 其实更常用的路径是虚拟环境的路径, 依赖就不一起打包了而是放在虚拟环境里 `-p {PATH_TO_VENV}/bin/python`

#### 场景 2

> 将代码打包成跨平台 + 跨 Python 版本的工具

使用延迟安装模式 `lazy install`

1. 同场景 1 的情况, 只不过参数里加入了一个 `-d`
   1. `python -m zipapps -c -d -a entrypoint.py -m entrypoint:main -o crawler.py requests`
2. 打包之后的文件很小, 因为只包含 `entrypoint.py` 代码和一些其他 meta 信息
3. 执行的时候和之前一样
   1. `python3 crawler.py` 
4. 然而这次执行会先通过 `pip` 安装 `requests` 这个依赖
   1. 只会安装到临时缓存目录里, **不会影响全局**
   2. 只会在首次运行时候安装, 之后就算多次打包, 如果依赖的东西不变, 也**不会重新安装**
5. **WARNING**: 由于启动了 `-d` 模式, 默认的缓存路径由原本的 `./zipapps_cache/crawler` 变成了 `SELF/zipapps_cache/crawler`
   1. 当然可以手动改成别的 `-up=xxx`
   2. 这里的这个 `SELF` 是个内置变量
      1. SELF: 打包文件自身目录
      2. HOME: 当前用户的 HOME 目录
      3. TEMP: `tempfile.gettempdir()` 临时目录

#### 场景 3

> 代码与依赖分离

可以参考 `--zipapps` 参数的用法, 不太常用不再赘述

`python3 app.pyz --zipapps=venv1.pyz,venv2.pyz`

### 解决之前的问题

#### 问题 1

1. 默认路径已经变成了 `./zipapps_cache/{app_name}`
2. 当然也可以在打包时候通过 `-up` 自定义指定
   1. 也可以在**运行时**通过环境变量覆盖掉原本指定的路径
   2. 支持 `SELF/TEMP/HOME` 内置变量, 也可以使用 `./` 这种和当前工作目录有关的相对路径

#### 问题 2

1. 在不修改默认 `build_id` 的前提下, 每次打包判断是否解压缩是根据打包时间戳来决定的
2. 解压的时候, 不管时间戳怎么变, `-o` 指定的默认 app 名称将作为唯一路径, 不会新建目录
   1. 默认 `-o` 是 `app.pyz`

#### 问题 3

1. 像 `bottle` / `requests` 之类纯 Python 编写的依赖, 是不需要解压缩的
2. 如果遇到需要解压缩 `.so` 等文件, 可以通过 `-u` 参数来指定, 常用参数有
   1. `-u AUTO` 自动解压带 `.so` / `.pyd` 的依赖
   2. `-u file1.py,dir1` 解压指定的文件或文件夹, 一般只支持根目录的文件名
   3. `-u="*"` 解压所有文件, 这里注意**不能使用** `-u *` , 因为 Linux 上 `*` 是有特殊意义的, 不是普通字符串

#### 问题 4

1. `-d` 延迟安装这个参数就是为跨平台和跨版本准备的
2. 延迟安装的目录会根据当前解释器与操作系统名称来创建, 互相隔离
3. 目前 Python 版本隔离的精度是 2, 也就是 3.7 和 3.8 共用一个目录
   1. 如果需要调整精度, 可以使用 `-pva 3` 或者 `-pva 1` 来调大调小精度

#### 问题 5

1. 上面提到的场景 3 里面 `--zipapps` 参数即可, 后来发现这么用不是很优雅
   1. 不过快速导入其他 `pyz` 里面的代码的时候, 或者共享依赖的时候, 还是有点用的

## 小结

其实一开始打算参考一下 `shiv` 的源码直接 **fork**, 后来发现... 里面实在太复杂了, 只好硬啃官方文档有关 `zipapp` 和 `zipimport` 的内容自己整. 等有时间还是得看看 `shiv` 在底层有没有目前我没有想到的一些细节和优化, 毕竟我一个人能测试或者思维的局限性还是挺明显的.

生产环境已经投入使用, 稳定性方面还没出现问题, 期间断断续续 fix 了十几个 bug 并新增了挺多正好用到的功能.

简而言之, 开发 `Zipapps` 的初衷其实很简单: **我希望把 Python 程序打包给别人用的时候像普通软件一样简单.**

感兴趣的话, 欢迎来提 Issue: https://github.com/ClericPy/zipapps ~~, 不感兴趣的话, 估计也看不到这一行.~~
