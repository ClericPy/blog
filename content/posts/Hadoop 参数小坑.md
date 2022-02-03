---
title: "Hadoop 参数小坑"
date: 2022-02-03T19:13:28+08:00
description: ""
categories: Python
draft: false
---

- mapreduce.map.memory.mb=4096
  
  - 这个参数是设置 task 内存的参数, 但是有坑在里面, 如果想细致调整内存占用避免 OOM Kill, 还要使用下面几个参数
  
  - mapreduce.map.java.opts=-Xmx2600m
    
    - map 任务里 Java 程序命令行参数设置最大堆内存, 这个内存和 task 总内存的差值要留给 Java 代码文件相关内存来使用
    
    - 所以一般推荐二者差值在 200 ~ 400 mb 之间, 堆内存大小一般是 0.75 * task 内存
  
  - mapreduce.reduce.shuffle.input.buffer.percent
    
    - 这个参数默认一般是 0.7, 但是有时候内存比磁盘贵的时候, 设置为 0.1 可以节省大量堆内存

- mapreduce.map.speculative=false
  
  - 这个参数默认是开启状态, 用途是预测执行逻辑, 同一个 job 下的某一个 task, 同时启动多个实例来运行, 以避免某个节点资源不足 (比如 CPU 忙碌或者网络带宽不足) 导致的某个任务执行过久拖累其他任务
    
    - 也就是在资源允许的情况下, 同一个任务启动两个, 先执行完的会发信号 kill 掉还没执行完毕的
    
    - 最大的坑就是两个地方
      
      - 会额外占用多余的资源
      
      - **非幂等** 类型的任务会出问题
  
  - 同理还有一个 mapreduce.reduce.speculative=false

- mapreduce.map.maxattempts=1
  
  - 任务最大尝试次数, 默认最多 4 次尝试(包含出错那次)
  
  - 坑
    
    - **非幂等** 任务重试会有问题
    
    - 代码或者输入本身就有问题的话, 不管怎么重试都是浪费时间白折腾
  
  - 同理也有 mapreduce.reduce.maxattempts=1

- mapreduce.job.reduce.slowstart.completedmaps=1.0
  
  - reduce 预热机制, 主要目的就是在 map 完成一定百分比的情况下提前把 reduce 资源申请下来, 减少切换状态及冷启动虚拟机的等待
    
    - 默认值 0.05 也就是 20 个 map 任务里只要完成一个就申请 reduce 容器资源
  
  - 有些 map 任务实际上会因为很多因素导致执行时间超长, reduce 资源申请下来却要等待很长时间不使用, 无疑是一种浪费
    
    - 例如 map 输入的 gz 文件有的很小有的巨大, 解压缩要很多时间
    
    - 比如 map 任务里各种奇怪的 sleep, 不是纯计算

- stream.non.zero.exit.is.failure=false
  
  - 非 0 状态码的退出是否算作失败
    
    - 有的场景失败也没事, 不需要重试

- mapreduce.map.failures.maxpercent=1
  
  - 允许的 map 任务失败比例, 一般不怎么用到

- mapreduce.job.maps=10
  
  - 这个参数控制输入文件拆分的 map 任务数量
    
    - 但是 gz 文件不是 splitable 的, 所以如果输入都是 gz 的话, 这个参数遇到输入文件数超过设置值时不生效
  
  - mapreduce.job.running.map.limit
    
    - 相对而言, 控制并发数量有些时候更有用一点

- 
