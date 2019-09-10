# -*- coding: UTF-8 -*-
"""
操作系统安全加固脚本
Author: 赵明明
"""
import os

from color import green, red
from system_config import Prop, show_colorful, padding, modify_optional


def info(msg):
    print(green(msg))


def password_check():
    """
    口令检测 /etc/shadow
    """
    prefix = "口令检测"
    pad = padding(80, prefix)
    try:
        f = open("/etc/shadow", "rb")
        context = f.read()
        f.close()
        correct = True
        for line in context.splitlines():
            arr = line.split(b":")
            if arr[1] == "":
                correct = False
                print("%s %s [%s]" % (prefix, pad, red("'%s'密码为空" % arr[0])))
            elif arr[2] == "0":
                correct = False
                print("%s %s [%s]" % (prefix, pad, red("'%s'UID为0" % arr[0])))
        if correct:
            print("%s %s [%s]" % (prefix, pad, green("通过")))
    except IOError:
        print("%s %s [%s]" % (prefix, pad, red("文件不存在")))


def path_check():
    """
    系统路径检测
    """
    path = str(os.environ.get("PATH"))
    prefix = "系统路径检测"
    if path.find('.:') == -1:
        print("%s %s [%s]" % (prefix, padding(80, prefix), green("通过")))
    else:
        print("%s %s [%s]" % (prefix, padding(80, prefix), red("不通过")))


def ls(pattern_file):
    pipe = os.popen('ls ' + pattern_file)
    lines = pipe.read().splitlines()
    pipe.close()
    return lines


if __name__ == "__main__":
    info("**************************************************************************************************")
    info("***********************************      操作系统安全加固      ***********************************")
    info("**************************************************************************************************")

    info("1.安全配置检测 ...................................................................................")
    # 密码检测
    password_check()
    # path检测
    path_check()

    # DNS相关
    dsn_props = [
        Prop("域名解析顺序", "/etc/host.conf", "order", "local,bind4"),
        Prop("允许一个主机对应多个IP", "/etc/host.conf", "multi", "on"),
        Prop("禁止SSH使用域名服务", "/etc/ssh/sshd_config", "UseDNS", "yes")]
    # 网络参数
    net_props = [
        Prop("最大文件句柄数(连接数)", "/etc/sysctl.conf", "fs.file-max", "65536", " = ", " *= *"),
        Prop("端口范围", "/etc/sysctl.conf", "net.ipv4.ip_local_port_range", "1024 65500", " = ", " *= *"),
        Prop("TCP允许TIME-WAIT状态的sockets用于新的连接", "/etc/sysctl.conf", "net.ipv4.tcp_tw_reuse", "1", " = ", " *= *"),
        Prop("TCP快速回收TIME-WAIT状态的sockets", "/etc/sysctl.conf", "net.ipv4.tcp_tw_recycle", "0", " = ", " *= *"),
        Prop("TCP连接空闲至发送第一次探针的时间间隔", "/etc/sysctl.conf", "net.ipv4.tcp_keepalive_time", "600", " = ", " *= *")]
    # 进程数
    proc_props = [Prop("打开文件数", "/etc/security/limits.conf", "*  -  nofile", "65536", " ", " +", 4)]
    files = ls('/etc/security/limits.d/*-nproc.conf')
    for filepath in files:
        filename = filepath[filepath.rfind('/') + 1:]
        proc_props.append(Prop("普通用户创建进程数(" + filename + ")", filepath, "* soft nproc", "5120", " ", " +", 4))
        proc_props.append(Prop("root用户创建进程数(" + filename + ")", filepath, "root soft nproc", "unlimited", " ", " +", 4))
    # 账户安全
    account_props = [
        Prop("超时时间", "/etc/profile", "export TMOUT", "180", "=", "="),
        Prop("root远程登录", "/etc/securetty", "CONSOLE", "/dev/tty01", " = ", " *= *"),
        Prop("密码过期天数", "/etc/login.defs", "PASS_MAX_DAYS", "90"),
        Prop("密码最小长度", "/etc/login.defs", "PASS_MIN_LEN", "8"),
        Prop("过期前警告天数", "/etc/login.defs", "PASS_WARN_AGE", "10")]
    # OpenSSH配置
    ssh_props = [
        Prop("SSH协议版本", "/etc/ssh/sshd_config", "Protocol", "2"),
        Prop("SSH严格模式", "/etc/ssh/sshd_config", "StrictModes", "yes"),
        Prop("不允许root用户SSH登录", "/etc/ssh/sshd_config", "PermitRootLogin", "no"),
        Prop("SSH打印上次登录日志", "/etc/ssh/sshd_config", "PrintLastLog", "yes"),
        Prop("SSH不允许空密码", "/etc/ssh/sshd_config", "PermitEmptyPasswords", "no")]
    # 其它
    other_props = [
        Prop("输出历史命令记录数", "/etc/profile", "HISTSIZE", "2", "=", "="),
        Prop("保留的历史命令总数", "/etc/profile", "HISTFILESIZE", "2", "=", "="),
        Prop("开启日志审核", "/etc/rsyslog.conf", "authpriv.*", "/var/log/secure")]

    # 展示结果
    show_colorful(dsn_props)
    show_colorful(net_props)
    show_colorful(proc_props)
    show_colorful(account_props)
    show_colorful(ssh_props)
    show_colorful(other_props)

    info("2.安全配置修复 ................................................................................")
    # 进行修复
    modify_optional(dsn_props)
    modify_optional(net_props)
    modify_optional(proc_props)
    modify_optional(account_props)
    modify_optional(ssh_props)
    modify_optional(other_props)

    info("3. 展示修复结果 ................................................................................")
    # 再次展示
    show_colorful(dsn_props)
    show_colorful(net_props)
    show_colorful(proc_props)
    show_colorful(account_props)
    show_colorful(ssh_props)
    show_colorful(other_props)
