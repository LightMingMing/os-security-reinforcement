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
from os_specification import Spec, display_colorful, modify_optional, promised


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

def read_os_conf():
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


def yum_proxy_conf(proxy, proxy_username="", proxy_password=""):
    yum_specs = []
    if proxy != "":
        yum_specs.append(Spec("yum代理", "/etc/yum.conf", "proxy", proxy, "=", "="))
        if proxy_username != "":
            yum_specs.append(Spec("用户名", "/etc/yum.conf", "proxy_username", proxy_username, "=", "="))
        if proxy_password != "":
            yum_specs.append(Spec("用户密码", "/etc/yum.conf", "proxy_password", proxy_password, "=", "="))
        display_colorful(yum_specs)
        modify_optional(yum_specs)


def software_install():
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
    # TODO zabbix
    """


def execute_command(command):
    f_open = os.popen(command)
    output = f_open.read()
    f_open.close()
    return output


def con_uuid_list():
    """系统连接的uuid集合"""
    uuid_list = []
    con_context = execute_command("nmcli connection show")
    print(con_context)
    lines = con_context.splitlines()
    uuid_head_idx = lines[0].find("UUID")
    for line in lines:
        uuid_tail_idx = line.find(" ", uuid_head_idx)
        uuid = line[uuid_head_idx:uuid_tail_idx]
        if uuid != "UUID":
            uuid_list.append(uuid)
    return uuid_list


def modify_dns_conf_optional(dns_conf):
    exp_dns_list = re.split(" +", dns_conf)
    print(green("期望DNS配置:"))
    print(exp_dns_list)

    # 查询当前配置的DNS
    context = execute_command("nmcli dev show | grep IP4.DNS")
    act_dns_list = []
    for act_dns in context.splitlines():
        act_dns_list.append(re.split(" +", act_dns, 2)[1])
    print(green("系统实际DNS配置:"))
    print(act_dns_list)

    # 比对
    need_modify = False
    for exp_dns in exp_dns_list:
        if exp_dns not in act_dns_list:
            need_modify = True
            break

    # 获取所有连接
    if need_modify:
        # 修改连接的DNS, 并生效
        for uuid in con_uuid_list():
            if promised(green("是否修改连接'%s'的DNS ? " % uuid)):
                os.system("nmcli connection modify %s ipv4.dns \"%s\"" % (uuid, dns_conf))
                os.system("nmcli connection up %s" % uuid)
    else:
        print(green("DNS配置正确, 不需要更改"))


def sync_system_time(chrony_server_list):
    """
    同步系统时间
    1. 获取/etc/chrony.conf中所有server
    2. 与chrony_server_list进行比对
    3. 注释掉不期望的server, 添加未配置的server
    """


if __name__ == "__main__":
    os_dict = read_os_conf()
    print(os_dict)

    # yum代理
    yum_proxy_conf(os_dict['yum.proxy'], os_dict['yum.proxy.username'], os_dict['yum.proxy.password'])

    # 软件安装
    software_install()

    # DNS配置
    modify_dns_conf_optional(os_dict['name.servers'])

    # TODO 系统时间同步
