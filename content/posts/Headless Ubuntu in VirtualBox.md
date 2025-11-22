---
title: "Headless Ubuntu in VirtualBox"
date: 2025-11-22T11:28:55+08:00
description: ""
categories: Python
draft: false
---


-   策略  
    
    -   无头虚拟机 + SSH  
        
        -   VirtualBox Headless  
            
        
        -   Ubuntu Server LTS  
            
        
        -   Mobaxterms（SSH）  
            
    
    -   空闲时资源占用：内存 60~200MB，磁盘 550MB  
        
-   步骤  
    
    -   安装 VBOX  
        -   [https://www.virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads)  
            
    
    -   安装Ubuntu  
        -   下载服务器 LTS 版本镜像 ISO  
            -   [https://cn.ubuntu.com/server](https://cn.ubuntu.com/server)  
                
    
    -   VBOX 新建虚拟机  
        
        -   选择镜像  
            
        
        -   自动安装  
            
            -   ① 设置个简单的用户名、密码  
                
            
            -   ② 其他默认即可  
                
        
        -   磁盘20GB足以，动态扩容（我配的80GB）  
            
        
        -   内存2GB 足以，随时可调整（我分配了8GB）  
            
        
        -   CPU 2 核够用，随时可调整（我分配了4）  
            
        
        -   如果选中 - 安装增强功能，可能会导致什么失败  
            -   如果不选中，共享文件夹可能不好用  
                
        
        -   点下一步，就会进入自动安装  
            -   安装完毕的时候可能看不出来，自己按几下回车发现可以输入命令就表示结束了  
                
    
    -   关机 - 正常关机  
        
    
    -   修改网络设置  
        
        -   右键虚拟机 - 设置 - 网络 - 继续使用 NAT  
            
        
        -   端口转发  
            
            -   名称：ssh  
                
            
            -   协议：TCP  
                
            
            -   主机IP：127.0.0.1  
                
            
            -   主机端口：10022  
                
            
            -   子系统IP：不填  
                
            
            -   子系统端口：22  
                
    
    -   启动 ssh 服务  
        
        -   双击虚拟机开机  
            
        
        -   输入帐号，密码  
            
        
        -   安装 ssh-server  
            
            -   sudo apt update  
                
            
            -   sudo apt install openssh-server -y  
                
            
            -   sudo systemctl enable ssh  
                
            
            -   sudo systemctl start ssh  
                
            
            -   sudo systemctl status ssh  
                
        
        -   关机 - 正常关机  
            
    
    -   无头模式启动虚拟机  
        -   右键虚拟机 - 启动 - 无界面模式启动  
            
            -   想使用的时候都用这个方式，或命令行方式启动  
                -   关闭和上面一样，关机 - 正常关机，或者ssh的时候命令行关机  
                    -   a. sudo poweroff  
                        
            
            -   无头启动，不需要登录，ssh 那边用密码登录  
                
    
    -   通过 ssh 连接它  
        
        -   ssh 127.0.0.1 -p 10022  
            -   上面设置的端口转发  
                
        
        -   mobaxterm 设置默认 execute  
            -   tmux a ||tmux  
                -   通过 tmux 保留上次登录的操作  
                    
        
        -   uv  
            -   curl -LsSf https://astral.sh/uv/install.sh | sh  
                
    
    -   免密码sudo  
        -   以有sudo权限用户登录，执行  
            
            -   sudo visudo  
                
            
            -   在 /etc/sudoers 文件尾部  
                -   your_real_user_id ALL=(ALL) NOPASSWD:/bin/su  
                    
-   FAQ  
    
    -   共享文件夹在虚拟机里没权限  
        -   将当前用户加入vboxsf组  
            
            -   sudo usermod -aG vboxsf $(whoami)  
                
            
            -   然后重启Linux虚拟机  
                
    
    -   宿主机-虚拟机互传文件  
        
        -   mobaxterm 自带的ssh旁边就有文件管理器，直接拖进去拖出来  
            
        
        -   或者用 共享文件夹  
            
    
    -   解决国内 docker pull 的 timeout  
        
        -   当然前提是安装了 docker  
            -   sudo apt install [docker.io](http://docker.io)  
                
        
        -   /etc/docker/daemon.json  
            
            -   如果没权限，则随便写进个文件，然后 sudo mv 1.json /etc/docker/daemon.json  
                
            
            -   {  
                
            
            -   "registry-mirrors": [  
                
            
            -   "https://docker.m.daocloud.io"  
                
            
            -   ]  
                
            
            -   }  
                
        
        -   sudo systemctl restart docker.service  
            
    
    -   宿主机 <-> 虚拟机 网络互通  
        
        -   NAT 模式联网时，宿主机访问虚拟机  
            -   端口转发进行配置：设置 - 网络 - 端口转发  
                -   新建一个规则，主机 IP 和子系统 IP 可以留空，直接填写两个端口号  
                    -   就是简单的 127.0.0.1:port 就会转发到虚拟机里的网络地址  
                        
        
        -   虚拟机访问宿主机的服务  
            -   通过 10.0.2.2:port 即可，该 ip 是虚拟机里默认分配的 NAT 网关也就是宿主机的地址  
                -   即：默认宿主机的 127.0.0.1 就是虚拟机里的 10.0.2.2  
                    
    
    -   docker 命令免 sudo  
        -   sudo usermod -aG docker $USER  
            -   重启终端  
                
    
    -   非本机登录机器  
        -   端口转发把 10022 那个 ssh 端口主机 IP 的 127.0.0.1 改成局域网 IP  
            -   或使用新端口  
                
    
    -   虚拟机系统迁移到其他电脑  
        -   vbox 导出、导入

> 文章来源: https://wr5w8p13b8.feishu.cn/mindnotes/VDA9bC4v6muG7JnawlrchiGjnGd
<!-- 格式转换: [Markdown](https://stackedit.cn/app#) -->
