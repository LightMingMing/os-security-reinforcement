# -*- coding: UTF-8 -*-
"""
资源resource相关
"""
import os

from tool.sys import os_version


def read_os_conf():
    """读取配置文件"""
    os_conf_dict = {}
    os_conf_file = open("resources/os.conf")
    os_conf_list = os_conf_file.read().splitlines()
    os_conf_file.close()
    for os_conf in os_conf_list:
        if os_conf.startswith('#') or os_conf.find("=") == -1:
            continue
        kv = os_conf.split("=", 2)
        os_conf_dict[kv[0]] = kv[1]
    return os_conf_dict


def tar_file_path(prefix):
    files = os.listdir('resources/tar')
    for f in files:
        if f.startswith(prefix):
            return 'resources/tar/' + f
    return ""


def rpm_file_path(prefix):
    os_v = os_version()
    if os_v == 7:
        suffix = "el7.x86_64.rpm"
    elif os_v == 6:
        suffix = "el6.x86_64.rpm"
    else:
        return ""
    files = os.listdir('resources/rpm')
    for f in files:
        if f.startswith(prefix) and f.endswith(suffix):
            return 'resources/rpm/' + f
    return ""


def file_name(file_path):
    return file_path[file_path.rfind('/') + 1:]
