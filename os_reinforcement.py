# -*- coding: UTF-8 -*-
"""
操作系统安全加固脚本
Author: 赵明明
TODO test
"""
import re
import os
from system_config import Prop


def red(s):
    return "\033[31m" + s + "\033[0m"


def yellow(s):
    return "\033[33m" + s + "\033[0m"


def green(s):
    return "\033[34m" + s + "\033[0m"


# 蓝色打印
def info(msg):
    print "\033[34m%s\033[0m" % msg.decode('utf-8')


# 黄色打印
def debug(msg):
    print "\033[33m%s\033[0m" % msg


# 红色打印
def warn(msg):
    print "\033[31m%s\033[0m" % msg


def find(file_path, prefix):
    try:
        f = open(file_path, "rb")
        context = f.read()
        f.close()
        lines = context.split("\n")
        for line in lines:
            if re.match(prefix, line):
                return line
    except IOError:
        warn("文件'%s'打开失败" % file_path)
        return None


def print_result(message_prefix, message_type):
    if message_type == 0:
        print "%-50s [%s]" % (message_prefix, yellow("NONE"))
    elif message_type == 1:
        print "%-50s [%s]" % (message_prefix, green("YES"))
    else:
        print "%-50s [%s]" % (message_prefix, warn("NO"))


def dns_order():
    """
    1.配置主机解析顺序 /etc/host.conf
        order local,bind4
    """
    line = find("/etc/host.conf", "order +")
    v = 0
    if line is not None:
        arr = re.split(" +", line, 2)
        if re.match("local, *bind4", arr[1]):
            v = 1
        else:
            v = 2
    print_result("域名解析顺序配置", v)


def allow_multi_ips_for_one_host():
    """
    2. 允许一个主机对应多个IP /etc/host.conf
        multi on
    """
    line = find("/etc/host.conf", "multi +")
    v = 0
    if line is not None:
        arr = re.split(" +", line, 2)
        if arr[1] == "on":
            v = 1
        else:
            v = 2
    print_result("一主机配置多个IP", v)


def dns_name_servers():
    """
    3. DNS服务器配置
    TODO 使用nmcli
    """


def forbid_ssh_use_dns():
    """
    4. 禁止SSH使用域名解析服务 /etc/ssh/sshd_config
        UseDNS no
    """
    line = find("/etc/ssh/sshd_config", "UseDNS +")
    v = 0
    if line is not None:
        arr = re.split(" +", line, 2)
        if arr[1] == "no":
            v = 1
        else:
            v = 2
    print_result("UseDNS is no ?", v)


def start_dns_cache():
    """
    5. 开启DNS Cache功能
    systemctl start nscd
    systemctl enable nscdfi
    TODO
    """


def sys_ctl_settings():
    """
    网络参数配置 /etc/sysctl.conf
        fs.file-max = 65536
        net.ipv4.ip_local_port_range = 1024 65500
        net.ipv4.tcp_tw_reuse = 1
        net.ipv4.tcp_tw_recycle = 0
        net.ipv4.tcp_keepalive_time = 600
    """
    sys_ctl_dict = {'fs.file-max': '65536',
                    'net.ipv4.ip_local_port_range': '1024 65500',
                    'net.ipv4.tcp_tw_reuse': '1',
                    'net.ipv4.tcp_tw_recycle': '0',
                    'net.ipv4.tcp_keepalive_time': '600'}
    for key in sys_ctl_dict:
        line = find("/etc/sysctl.conf", key + " +")
        v = 0
        if line is not None:
            arr = re.split(" *= *", line, 2)
            if arr[1] == sys_ctl_dict[key]:
                v = 1
            else:
                v = 2
        print_result("%s is %s ?" % (key, sys_ctl_dict[key]), v)


def sys_open_file_num_limit():
    """
    系统打开文件数 /etc/security/limits.conf
        *  -  nofile  65536
    """
    line = find("/etc/security/limits.conf", "* +- +nofile +")
    v = 0
    if line is not None:
        arr = re.split(" +", line, 4)
        if arr[3] == "65536":
            v = 1
        else:
            v = 2
    print_result("系统打开文件数", v)


def proc_num_limit():
    """
    进程数 /etc/security/limits.d/20-nproc.conf
        *          soft    nproc     5120
        root       soft    nproc     unlimited
    """
    line = find("/etc/security/limits.conf", "\\* +soft +nporc +")
    v = 0
    if line is not None:
        arr = re.split(" +", line, 4)
        if arr[3] == "5120":
            v = 1
        else:
            v = 2
    print_result("普通用户创建进程数", v)

    line = find("/etc/security/limits.conf", "root +soft +nporc +")
    v = 0
    if line is not None:
        arr = re.split(" +", line, 4)
        if arr[3] == "unlimited":
            v = 1
        else:
            v = 2
    print_result("root用户创建进程数", v)


def open_ssh_config():
    """
    OpenSSH相关配置
    """
    ssh_dict = {'Protocol': '2', 'StrictModes': 'yes', 'PermitRootLogin': 'no', 'PrintLastLog': 'yes',
                'PermitEmptyPasswords': 'no'}
    for key in ssh_dict:
        line = find("/etc/ssh/sshd_config", key + " +")
        v = 0
        if line is not None:
            arr = re.split(" +", line, 2)
            if arr[1] == ssh_dict[key]:
                v = 1
            else:
                v = 2
        print_result("%s is %s ?" % (key, ssh_dict[key]), v)


def empty_pass_check():
    """
    空口令,UID为0账户检测 /etc/shadow
    """
    try:
        f = open("/etc/shadow", "rb")
        context = f.read()
        f.close()
        lines = context.split("\n")
        for line in lines:
            arr = line.split(":")
            print arr
            if arr[1] == "":
                warn("%s 空口令" % arr[0])
            elif arr[2] == "0":
                warn("%s uid为0" % arr[0])
    except IOError:
        warn("文件'/etc/shadow'打开失败")


def sys_path_check():
    """
    root路径检测
    """
    path = str(os.environ.get("PATH"))
    if path.find('.:') == -1:
        print_result("root路径不包含':.'", 1)
    else:
        print_result("root路径不包含':.", 2)


def session_timout_check():
    """
    系统超时时间
    """
    line = find("/etc/profile", "export TMOUT=")
    v = 0
    if line is not None:
        arr = re.split("=", line, 2)
        if arr[1] == "180":
            v = 1
        else:
            v = 2
    print_result("TMOUT is 180 ?", v)


def root_remote_login_check():
    """
    root远程登录
    """
    line = find("/etc/security", "CONSOLE")
    v = 0
    if line is not None:
        arr = re.split(" *= *", line, 2)
        if arr[1] == "/dev/tty01":
            v = 1
        else:
            v = 2
    print_result("CONSOLE is /dev/tty01 ?", v)


def pass_strength_check():
    """
    密码强度检测
    """
    pass_dict = {'PASS_MAX_DAYS': '90', 'PASS_MIN_LEN': '8', 'PASS_WARN_AGE': '10'}
    for key in pass_dict:
        line = find("/etc/login.defs", key + " +")
        v = 0
        if line is not None:
            arr = re.split(" +", line, 2)
            if arr[1] == pass_dict[key]:
                v = 1
            else:
                v = 2
        print_result("%s is %s ?" % (key, pass_dict[key]), v)


def auth_pri_log():
    """
    日志审核 /etc/rsyslog.conf
        authpriv.*        /var/log/secure
    """
    line = find("/etc/rsyslog.conf", "authpriv\\.\\* +")
    v = 0
    if line is not None:
        arr = re.split(" +", line, 2)
        if arr[1] == "/var/log/secure":
            v = 1
        else:
            v = 2
    print_result("是否开启日志审核", v)


def show(prop):
    if prop.status == -2:
        print("%s %s  [%s]" % (prop.desc, prop.key, red("文件打开失败")))
    elif prop.status == -1:
        print("%s %s  [%s]" % (prop.desc, prop.key, red("配置错误, 期望'%s', 实际'%s'" % (prop.exp_val, prop.rel_val))))
    elif prop.status == 0:
        print("%s %s  [%s]" % (prop.desc, prop.key, yellow("未配置")))
    elif prop.status == 1:
        print("%s %s [%s]" % (prop.desc, prop.key, green("配置正确")))


if __name__ == "__main__":
    info("***************************************************************************************")
    info("******************************      操作系统安全加固     ********************************")
    info("***************************************************************************************")
    print()
    dns_order()
    allow_multi_ips_for_one_host()
    dns_name_servers()
    forbid_ssh_use_dns()
    start_dns_cache()

    sys_ctl_settings()
    sys_open_file_num_limit()
    proc_num_limit()

    open_ssh_config()

    empty_pass_check()
    sys_path_check()
    session_timout_check()
    root_remote_login_check()
    pass_strength_check()
    auth_pri_log()

    print "\n"

    dns_order = Prop("域名解析顺序", "/etc/host.conf", "order", "local,bind4")
    show(dns_order)

    allow_multi_ips_for_one_host = Prop("允许一个主机对应多个IP", "/etc/host.conf", "multi", "on")
    show(allow_multi_ips_for_one_host)

    forbid_ssh_use_dns = Prop("禁止SSH使用域名服务", "/etc/ssh/sshd_config", "UseDNS", "yes")
    show(forbid_ssh_use_dns)

    file_max = Prop("最大打开文件数", "/etc/sysctl.conf", "fs.file-max", "65536", " = ", " *= *")
    show(file_max)

    port_range = Prop("端口范围", "/etc/sysctl.conf", "net.ipv4.ip_local_port_range", "1024 65500", " = ", " *= *")
    show(port_range)

    tw_reuse = Prop("resue", "/etc/sysctl.conf", "net.ipv4.tcp_tw_reuse", "1", " = ", " *= *")
    show(tw_reuse)

    tw_recycle = Prop("", "/etc/sysctl.conf", "net.ipv4.tcp_tw_recycle", "0", " = ", " *= *")
    show(tw_recycle)

    tcp_keepalive_time = Prop("", "/etc/sysctl.conf", "net.ipv4.tcp_keepalive_time", "600", " = ", " *= *")
    show(tcp_keepalive_time)

    limits = Prop("", "/etc/security/limits.conf", "*  -  nofile", "65536", " ", " +", 4)
    show(limits)
