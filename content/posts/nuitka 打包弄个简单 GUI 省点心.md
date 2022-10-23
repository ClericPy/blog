---
title: "Nuitka 打包弄个简单 GUI 省点心"
date: 2022-10-23T11:47:39+08:00
description: ""
categories: Python
draft: false
---

> https://github.com/ClericPy/nuitka_simple_gui

长话短说, 以前用 pyinstaller 打包总是有各种 platform.dll 什么的问题, 后来改 nuitka 了, 半年前随手写了个 GUI 日常使用一下

暂时不上 pypi 了, 代码质量不太好

基本功能:

1. 常用命令行参数直接勾选, 不用动脑子记命令
2. Linux / Windows 应该都成功打包过
3. 不使用单文件模式, 因为和 pyinstaller 一样会在 tmp 目录产生缓存文件但不删除, 虽然可以自定义缓存目录, 但还是没必要
4. 非单文件编译, 输出目录
   1. 支持直接压缩成 zip 方便发送给别人, 也节省了体积
   2. 添加入口软链接(Windows), 省的进文件夹里找 exe 文件
   3. 依赖的第三方包会通过 `pip install lib -t xxx` 的方式直接放到输出目录里
      1. 节省编译时间, 否则有些 numpy 之类的包编译要很长时间
5. 图形界面即文档
   1. 直接下载下去运行就好了, 提前安装好 python 和 nuitka
   2. https://github.com/ClericPy/nuitka_simple_gui/blob/master/nuitkaui.pyw
