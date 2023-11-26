---
title: "pip.pyz 与 Windows 绿色版 Python app"
date: 2023-11-26T21:40:11+08:00
description: ""
categories: Python
draft: false
---

# 不说废话

## 文档

https://pip.pypa.io/en/stable/installation/#standalone-zip-application

## 下载地址
https://bootstrap.pypa.io/pip/pip.pyz

# 用途
Windows embeded python 安装 pip
1. 将 `嵌入式 python` 下载并解压缩到 `python-3.11.5-embed-amd64/`
2. 下载 `pip.pyz` 文件到 `python-3.11.5-embed-amd64/`
3. 在 `python311._pth`(根据版本号 `311` 可能是其他数字) 文件里写入
```
import site

pip.pyz
```
4. 这样就可以直接 pip 安装依赖了 `./python.exe -m pip install xxx`
