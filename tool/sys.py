# -*- coding: UTF-8 -*-
"""
系统相关
Author: 赵明明
"""
import socket
import os


def get_host():
    """获取主机IP"""
    return socket.gethostbyname(socket.gethostname())


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
