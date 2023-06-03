---
title: "尝鲜绿色版解释器, 以及打包分发 Python 软件"
date: 2023-06-03T12:27:12+08:00
description: "python-build-standalone +PyOxy +zipapps"
categories: Python
draft: false
---

### 背景:

期待已久的绿色版 Python 解释器终于成熟可用, 目前体验地址是 [Releases · indygreg/python-build-standalone · GitHub](https://github.com/indygreg/python-build-standalone/releases) python-build-standalone 项目 release 2023.5.7, 包含 mac/linux/win32 多平台可用.

所以分享一下未来一段时间内使用 Python 语言编写应用后分发到各平台的简单方式, 如果比较在乎保护源码, 则可以考虑使用 pyinstaller / nuitka 编译的方式来发布. 两者我都写过简单 UI 来搞, 目前主要使用 nuitka, 有兴趣可以参考之前写的一个 nuitka 打包 GUI: https://github.com/ClericPy/nuitka_simple_gui , 简单这个 GUI 默认只编译你核心代码, 依赖是通过外部安装的方式打包起来, 最后输出 zip 和快捷软链给用户

### 过程:

以 Windows 平台为例, linux 等其他平台其实也很简单, 毕竟解释器各平台都有, zipapps 的 pyz 文件也可以跨平台.

1. 下载想要的解释器, 版本解释
   
   1. 主要找文件名里带 `install_only ` 的, 这个不是让你拿去自己编译, 而是直接使用
   2. Windows 的是 `pc-windows-msvc-shared` 标记
      1. 举例
         1. [cpython-3.11.3+20230507-i686-pc-windows-msvc-shared-install_only.tar.gz](https://github.com/indygreg/python-build-standalone/releases/download/20230507/cpython-3.11.3+20230507-i686-pc-windows-msvc-shared-install_only.tar.gz)
         2. Linux
            1. [cpython-3.11.3+20230507-aarch64-unknown-linux-gnu-install_only.tar.gz](https://github.com/indygreg/python-build-standalone/releases/download/20230507/cpython-3.11.3+20230507-aarch64-unknown-linux-gnu-install_only.tar.gz)
         3. Darwin
            1. [cpython-3.11.3+20230507-aarch64-apple-darwin-install_only.tar.gz](https://github.com/indygreg/python-build-standalone/releases/download/20230507/cpython-3.11.3+20230507-aarch64-apple-darwin-install_only.tar.gz)
   3. 也可以找 pgo 优化版, 性能有些提升, 兼容性目前没发现有什么问题
      1. 就是带 `pgo` 字段的文件名
      2. 但是要注意需要解压缩 `.zst` 压缩文件, 不知道为什么不用 7z
      3. 举例
         1. [cpython-3.11.3+20230507-i686-pc-windows-msvc-shared-pgo-full.tar.zst](https://github.com/indygreg/python-build-standalone/releases/download/20230507/cpython-3.11.3+20230507-i686-pc-windows-msvc-shared-pgo-full.tar.zst) 

2. 这里就选择 `pgo` 优化过的 Windows 平台路径
   
   1. 解压缩拿到 python 文件夹, 里面包含 python.exe 文件
   2. 当前目录结构 app/python

3. 要分发的软件代码分两种情况
   
   1. 一种是没有第三方依赖的情况
      1. 单纯一个 py/pyw 文件的话, 直接放在 app 目录下面
         1. 例如 app.py
      2. 如果是一个包, 则使用 zipapps 打包成一个 pyz 文件
   2. 一种是需要第三方依赖的代码
      1. 使用 zipapps 将依赖和代码打包成一个 pyz 文件
         1. 因为会将解释器一起打包过去, 所以不使用 `-d` 惰性安装依赖, 直接安装就好了
         2. `python/python.exe -m pip install zipapps -U`
         3. `python/python.exe -m zipapps -a script.py -m script -u=* -up $SELF/cache requests --no-cache-dir`
   3. 当然, 也可以直接用 `pip` 安装依赖然后执行代码
      1. `python/python.exe -m pip install -r requests`
      2. 用 zipapps 主要目的是为了不污染解释器默认环境, 可以一个解释器启动多个 app 而环境隔离

4. 编写执行入口
   
   1. Windows 简单使用 bat 文件
      1. `start python/python.exe app.pyz`
         1. `start python/python.exe app.pyz`
         2. 或者用 pythonw.exe
   2. 其他平台考虑 run.sh

5. 完整代码与文件夹结构
   
   1. script.py
      
      1. ```python
         import requests
         import time
         ```

         print(requests.get('http://bing.com').text)
         time.sleep(3)
         ```

2. 目录结构
   
   1. ```py
      └─python
          ├─DLLs
          ├─include
          │  ├─cpython
          │  └─internal
          ├─Lib
          │  ├─site-packages
      └─app.pyz
      └─run.bat
      └─script.py
      ```

3. bat 命令隐藏黑框
   
   1. 
      
      1. 彻底隐藏: 创建 bat 文件的快捷方式, 快捷方式属性里
         
         1. <mark>**运行方式 - 最小化**</mark>
      
      2. 启动时隐藏: start 命令添加 /min 参数
      
      3. 必要时候使用 pythonw.exe 启动

### 性能

1. #### 三个 Python 版本简单测试下性能损失
   
   1. 平台: Windows10
   
   2. Python 版本: 官方 CPython3.11, 绿色版 Python3.11, 绿色版 Python3.11(pgo)
   
   3. 测试代码
      
      1. ```python
         import sys
         from timeit import timeit
         ```

         def fib(n):
             if n <= 1:
                 return n
             else:
                 return fib(n - 1) + fib(n - 2)
    
    
         def test():
             fib(10)
    
    
         print(sys.executable, round(timeit(test, number=100000), 6))
         ```

4. 测试结果
   
   1. ```md
      # 官方 CPython3.11
      D:\python311\python3.exe 1.178743
      # 绿色版 Python3.11
      D:\downloads\python3\3.11\python.exe 1.143648
      # 绿色版 pgo Python3.11
      D:\downloads\python3\3.11pgo\python.exe 1.037657
      ```

5. 结论
   
   1. 官方版中规中矩, 用的 3.11.0, 两个绿色版是 3.11.3
   
   2. 绿色版 3.11 略微提升一点
   
   3. 绿色版 pgo 优化后会比官方提升 10% 左右
   
   4. 没发现明显性能损失
