# -*- coding: UTF-8 -*-
"""
操作系统基础软件安装
1. 基础环境: vim, gcc, iftop, firewall-cmd, nslookup, iperf, telnet, zip, tar, lvm2, nmcli
2. 运行环境: nginx, java
3. 监控: zabbix

Author: 赵明明
"""

import os
import re

from color import green
from os_specification import Spec, display_colorful, modify_optional


# TODO
# 1. 配置yum源代理
# 2. 安装各个所需软件, 需要确定各个软件的安装方式
# 3. nmcli配置DNS服务器
# 4. 系统时间同步，日期同步
# 5. 系统兼容性 CentOS 6、CentOS 7、Ubuntu

# TODO 测试环境安装结果, 看看要怎么解决
# iftop, iperf 安装不成功 需要EPEL安装源 yum install epel-release, 安装后还要配置可用的epel镜像 /etc/yum.repos.d/epel.repo
# CentOS 7上可以安装iperf3
# nginx安装不成功, 需要配置yum源? 还是直接wget下载压缩包
# nginx, java 版本问题

def load_conf_dict():
    """读取配置文件"""
    os_conf_dict = {}
    os_conf_file = open("os.conf")
    os_conf_list = os_conf_file.read().splitlines()
    os_conf_file.close()
    for os_conf in os_conf_list:
        if os_conf.startswith('#') or os_conf.find("=") == -1:
            continue
        kv = os_conf.split("=", 2)
        os_conf_dict[kv[0]] = kv[1]
    return os_conf_dict


if __name__ == "__main__":
    os_dict = load_conf_dict()
    print(os_dict)

    # yum代理
    yum_specs = []
    proxy = os_dict['yum.proxy']
    if proxy != "":
        yum_specs.append(Spec("yum代理", "/etc/yum.conf", "proxy", proxy, "=", "="))
        proxy_username = os_dict['yum.proxy.username']
        if proxy_username != "":
            yum_specs.append(Spec("用户名", "/etc/yum.conf", "proxy_username", proxy_username, "=", "="))
        proxy_password = os_dict['yum.proxy.password']
        if proxy_password != "":
            yum_specs.append(Spec("用户密码", "/etc/yum.conf", "proxy_password", proxy_password, "=", "="))
    display_colorful(yum_specs)
    modify_optional(yum_specs)

    # 软件安装
    """
    os.system('yum install vim')
    os.system('yum install gcc')
    os.system('yum install iftop')  # TODO
    os.system('yum install firewalld')
    os.system('yum install bind-utils')  # nslookup
    os.system('yum install iperf3')  # TODO
    os.system('yum install telnet')
    os.system('yum install tar')
    os.system('yum install zip')
    os.system('yum install lvm2')
    os.system('yum install nginx')  # TODO
    os.system('yum install java')  # TODO
    """

    # DNS配置
    # 查询已配置的DNS
    # $ nmcli dev show | grep IP4.DNS
    f = os.popen("nmcli dev show | grep IP4.DNS")
    context = f.read()
    f.close()
    act_dns_list = []
    for line in context.splitlines():
        arr = re.split(" +", line, 2)
        act_dns_list.append(arr[1])

    print(green("系统实际DNS配置:"))
    print(act_dns_list)

    exp_dns_conf = os_dict['name.servers']
    exp_dns_list = re.split(" +", exp_dns_conf)
    print(green("期望DNS配置:"))
    print(exp_dns_list)

    # 是否需要配置
    need_modify = False
    for exp_dns in exp_dns_list:
        if exp_dns not in act_dns_list:
            need_modify = True
            break

    # CentOS 7 获取所有连接的UUID
    # $ nmcli connection show
    # NAME         UUID                                  TYPE      DEVICE
    # System eth0  5fb06bd0-0bb0-7ffb-45f1-d6edd65f3e03  ethernet  eth0
    if need_modify:
        print(green("进行DNS配置"))
        uuid_list = []
        f = os.popen("nmcli connection show")
        con_show_context = f.read()
        print(con_show_context)
        lines = con_show_context.splitlines()
        f.close()
        uuid_head_idx = lines[0].find("UUID")
        for line in lines:
            uuid_tail_idx = line.find(" ", uuid_head_idx)
            uuid = line[uuid_head_idx:uuid_tail_idx]
            if uuid != "UUID":
                uuid_list.append(uuid)
        # 配置连接DNS并生效
        # $ nmcli connection modify $uuid  ipv4.dns "*.*.*.* *.*.*.*"
        # $ nmcli connection up $uuid
        for uuid in uuid_list:
            os.system("nmcli connection modify %s ipv4.dns \"%s\"" % (uuid, exp_dns_conf))
            os.system("nmcli connection up %s" % uuid)
    else:
        print(green("不需要DNS配置"))

    # TODO 系统时间同步
