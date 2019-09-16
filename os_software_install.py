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

from color import green, red
from os_specification import Spec, display_colorful, modify_optional, promised


# 1. 配置yum源代理
# 2. 安装各个所需软件, 需要确定各个软件的安装方式
# 3. nmcli配置DNS服务器
# 4. 系统时间同步，日期同步
# 5. TODO 系统兼容性 CentOS 6、CentOS 7、Ubuntu

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


def yum_install(name):
    print(green("准备安装'%s'......" % name))
    os.system("yum install %s" % name)


def os_version():
    rpm_cmd = execute_command('command -v rpm')
    if len(rpm_cmd) > 0:
        return int(execute_command('rpm -q centos-release | cut -d- -f3'))
    # TODO 支持ubuntu版本
    return 0


def rpm_file_path(prefix, suffix):
    files = os.listdir('rpm')
    for f in files:
        if f.startswith(prefix) and f.endswith(suffix):
            return 'rpm/' + f
    return ""


def rpm_install_iftop():
    os_v = os_version()
    file_path = ""
    if os_v == 7:
        file_path = rpm_file_path("iftop", "el7.x86_64.rpm")
    elif os_v == 6:
        file_path = rpm_file_path("iftop", "el6.x86_64.rpm")
    if file_path is not None and len(file_path) > 0:
        if promised(green("是否安装'%s' ? " % file_path)):
            execute_command('rpm -Uvh %s' % file_path)
            yum_install('iftop')
    else:
        print(red("'iftop'安装包不存在"))


def rpm_install_iperf():
    os_v = os_version()
    file_path = ""
    if os_v == 7:
        file_path = rpm_file_path("iperf", "el7.x86_64.rpm")
    elif os_v == 6:
        file_path = rpm_file_path("iperf", "el6.x86_64.rpm")
    if file_path is not None and len(file_path) > 0:
        if promised(green("是否安装'%s' ? " % file_path)):
            execute_command('rpm -Uvh %s' % file_path)
            yum_install('iperf')
    else:
        print(red("'iperf'安装包不存在"))


def install_all_required_software():
    yum_install('vim')
    yum_install('gcc')
    yum_install('telnet')
    yum_install('tar')
    yum_install('zip')
    yum_install('lvm2')
    yum_install('firewalld')
    yum_install('bind-utils')  # nslookup
    yum_install('java')
    rpm_install_iftop()
    rpm_install_iperf()
    # TODO nginx
    # TODO zabbix


def execute_command(command):
    f_open = os.popen(command)
    output = f_open.read()
    f_open.close()
    return output


def con_uuid_list():
    """系统连接的uuid集合"""
    uuid_list = []
    con_ctx = execute_command("nmcli connection show")
    print(con_ctx)
    lines = con_ctx.splitlines()
    if len(lines) > 0:
        uuid_head_idx = lines[0].find("UUID")
        for line in lines:
            uuid_tail_idx = line.find(" ", uuid_head_idx)
            uuid = line[uuid_head_idx:uuid_tail_idx]
            if uuid != "UUID":
                uuid_list.append(uuid)
    return uuid_list


def modify_dns_conf_optional(dns_conf):
    exp_dns_list = re.split(" +", dns_conf)
    print("期望DNS配置:")
    print(exp_dns_list)

    # 查询当前配置的DNS
    dns_ctx = execute_command("nmcli dev show | grep IP4.DNS")
    act_dns_list = []
    for act_dns in dns_ctx.splitlines():
        act_dns_list.append(re.split(" +", act_dns, 2)[1])
    print("系统实际DNS配置:")
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
        print("DNS配置正确, 不需要更改")


def sync_system_time(chrony_server_conf):
    """
    同步系统时间
    1. 获取/etc/chrony.conf中所有server
    2. 与chrony_server_list进行比对
    3. 注释掉不期望的server, 添加未配置的server
    """
    exp_server_list = re.split(" +", chrony_server_conf)
    print('期望时间服务器配置:')
    print(exp_server_list)

    chr_ctx = execute_command("cat /etc/chrony.conf | grep -n '^server'")  # -n 显示行号
    line_num_list = []
    act_server_list = []
    for line in chr_ctx.splitlines():
        arr = re.split(" +", line, 3)
        act_server_list.append(arr[1])
        line_num_list.append(arr[0][:arr[0].find(':')])  # 1:server 获取在文件中行号
    print('系统实际时间服务配置:')
    # print(chr_ctx)
    print(act_server_list)

    # 比对, 注释掉不期望的配置
    for idx in range(len(act_server_list)):
        act_server = act_server_list[idx]
        if act_server not in exp_server_list:
            if promised(green("不期望的时间服务器'%s', 是否需要将其注释 ? " % act_server)):
                line_num = line_num_list[idx]
                command = "sed -i '%ss/^/# /' /etc/chrony.conf" % line_num
                print(command)
                os.system(command)
    # 比对, 添加期望的配置
    insert_line_num = 1
    if len(line_num_list) != 0:
        insert_line_num = int(line_num_list[len(line_num_list) - 1])
    for exp_server in exp_server_list:
        if exp_server not in act_server_list:
            if promised(green("未配置时间服务器'%s', 是否配置 ? " % exp_server)):
                os.system("sed -i '%da server %s iburst' /etc/chrony.conf" % (insert_line_num, exp_server))


def set_system_timezone():
    """查看当前时区, 不是Asia/Shanghai则进行修改"""
    zone_ctx = execute_command("timedatectl status | grep zone")
    print("当前时区")
    print(zone_ctx)
    if zone_ctx.find('Asia/Shanghai') == -1:
        if promised(green("当前时区非'Asia/Shanghai', 是否进行配置 ? ")):
            os.system("timedatectl set-timezone Asia/Shanghai")
            os.system("chronyc -a makestep")
    else:
        print("时区配置正确, 不需要更改")


def password_less_login():
    if os.path.exists('id_rsa.pub'):
        if promised(green("是否进行免密登录配置 ? ")):
            os.system("mkdir -p ~/.ssh && chmod 700 ~/.ssh")
            os.system("cat id_rsa.pub | cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys")
    else:
        print(red("免密登录, 没有找到'id_rsa.pub'文件"))


def service_probes_and_shutdown_optional():
    service_ctx = execute_command('netstat -nlp -t -u')
    print(service_ctx)
    lines = service_ctx.splitlines()
    port_to_server_dict = {}
    for line in lines:
        arr = []
        if line.startswith('tcp'):
            arr = re.split(" +", line, 6)
        elif line.startswith('udp'):
            arr = re.split(" +", line, 5)
        if len(arr) != 0:
            local_address = arr[3]
            pid_and_name = arr[-1]
            port = local_address[local_address.rfind(':') + 1:]
            port_to_server_dict[port] = pid_and_name
    for port in port_to_server_dict:
        pid_and_name = port_to_server_dict[port]
        pid = pid_and_name[:pid_and_name.find('/')]
        name = pid_and_name[pid_and_name.find('/') + 1:]
        print("端口: %s 进程ID：%s 服务名: %s" % (port, pid, name))
        if port != "323" and port != "22":
            if promised('是否关闭该服务 ? '):
                os.system("kill -15 %s" % pid)
            # 有的服务可能关闭不了, 需要下面方式
            # systemctl stop service
            # systemctl disable service


def firewall_service_management():
    """防火墙服务管理"""
    # 启动防火墙
    os.system('systemctl start firewalld')
    # 查看允许的服务
    act_service_list = execute_command('firewall-cmd --list-services')[0:-1].split(" ")
    print(green("实际允许的服务:"))
    print(act_service_list)
    exp_service_list = ['ssh', 'zabbix-agent', 'chronyd']
    need_reload = False
    # 删除非期望的服务
    for act_service in act_service_list:
        if act_service not in exp_service_list and len(act_service) > 0:
            if promised(green("是否删除'%s'服务 ? " % act_service)):
                os.system('firewall-cmd --remove-service=%s --permanent' % act_service)
                need_reload = True
    # 添加期望的服务
    for exp_service in exp_service_list:
        if exp_service not in act_service_list:
            if promised(green("是否添加'%s'服务 ? " % exp_service)):
                if exp_service == 'chronyd':
                    # 自定义服务
                    os.system('firewall-cmd --new-service=chronyd --permanent')
                    os.system('firewall-cmd --service=chronyd --add-port=323/tcp --permanent')
                    os.system('firewall-cmd --service=chronyd --add-port=323/udp --permanent')
                    # 重新加载, 不然仍会服务无效
                    os.system('firewall-cmd --reload')
                    # 添加
                    os.system('firewall-cmd --add-service=chronyd --permanent')
                else:
                    os.system("firewall-cmd --add-service=%s --permanent" % exp_service)
                need_reload = True
    if need_reload:
        os.system('firewall-cmd --reload')


if __name__ == "__main__":
    os_dict = read_os_conf()
    print(os_dict)

    # yum代理
    print(green("1.yum代理配置 ................................................................................."))
    yum_proxy_conf(os_dict['yum.proxy'], os_dict['yum.proxy.username'], os_dict['yum.proxy.password'])

    # 软件安装
    print(green("2.软件安装 ...................................................................................."))
    install_all_required_software()

    # DNS配置
    print(green("3.DNS配置 ....................................................................................."))
    modify_dns_conf_optional(os_dict['name.servers'])

    # 系统时间同步
    print(green("4.系统时间同步 ................................................................................"))
    sync_system_time(os_dict['chrony.servers'])

    # 时区设置
    print(green("5.时区设置 ...................................................................................."))
    set_system_timezone()

    # 免密登录
    print(green("6.免密登录 ...................................................................................."))
    password_less_login()

    # 服务检测
    print(green("7.服务检测 ...................................................................................."))
    service_probes_and_shutdown_optional()

    # 防火墙
    print(green("8.防火墙服务管理 .............................................................................."))
    firewall_service_management()
