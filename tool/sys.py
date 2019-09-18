# -*- coding: UTF-8 -*-
"""
系统相关
Author: 赵明明
"""
import os
import socket


def get_host():
    """获取主机IP"""
    try:
        return socket.gethostbyname(socket.gethostname())
    except IOError:
        host = execute("ifconfig -a | grep inet | grep -v 127.0.0.1 | grep -v inet6 | awk '{print $2}'| tr -d 'addr:'")
        return host[0:-1]


def os_version():
    rpm_cmd = execute('command -v rpm')
    if len(rpm_cmd) > 0:
        return int(execute('rpm -q centos-release | cut -d- -f3'))
    # TODO 支持ubuntu版本
    return 0


def execute(command):
    """执行命令"""
    f_open = os.popen(command)
    output = f_open.read()
    f_open.close()
    return output
