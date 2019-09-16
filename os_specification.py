# -*- coding: UTF-8 -*-
"""
操作系统配置规范
Author: 赵明明
"""

import re

from tool.console import red, yellow, green, padding, promised
from tool.sys import execute


class Spec(object):
    """配置规范"""

    def __init__(self, desc, file_path, key, exp_val, interval=" ", pattern_split=" +", num_split=1):
        """
        初始化一个配置项, 并检测
        :param desc: 描述
        :param file_path: 配置文件路径
        :param key: 键值
        :param exp_val: 期望值
        :param interval: 间隔符
        :param pattern_split: 将配置分割获取实际值'rel_val'的正则表达式, 默认按照多个空格分隔即" +"
        :param num_split: 分割次数, 默认1次
        """
        self._desc = desc
        self._file_path = file_path
        self._key = key
        self._exp_val = exp_val
        self._act_val = None
        self._status = 0
        self._interval = interval
        # 从配置文件中匹配配置项的正则表达式
        self._pattern_prefix = re.compile(escape(self._key) + pattern_split)
        # 配置项分割正则表达式
        self._pattern_split = re.compile(pattern_split)
        self._num_split = num_split
        # 行号
        self._line_num = 0
        self.validate()

    @property
    def desc(self):
        return self._desc

    @property
    def file_path(self):
        return self._file_path

    @property
    def key(self):
        return self._key

    @property
    def exp_val(self):
        return self._exp_val

    @property
    def act_val(self):
        return self._act_val

    @property
    def status(self):
        """
        :return: 状态
            -2 表示文件操作异常, 文件可能不存在
            -1 实际配置与期望配置不一致
             0 未配置
             1 实际配置与期望配置一致
        """
        return self._status

    @property
    def line_num(self):
        return self._line_num

    def standard_config(self):
        return self._key + self._interval + self._exp_val

    def validate(self):
        try:
            f = open(self._file_path, "rb")
            context = f.read()
            f.close()
            self._line_num = 0
            for line in context.splitlines():
                self._line_num += 1
                if self._pattern_prefix.match(str(line)):
                    arr = self._pattern_split.split(str(line), self._num_split)
                    self._act_val = arr[self._num_split]  # arr[-1]
                    if self._exp_val == self._act_val:
                        # 期望配置
                        self._status = 1
                    else:
                        # 非期望配置
                        self._status = -1
                    return
            # 未配置
            self._line_num = 0
            self._status = 0
        except IOError:
            # 文件操作异常
            self._line_num = -1
            self._status = -2

    def modify(self):
        if self.status == -1:
            # command = "sed -n '%dc %s' %s" % (self.line_num, self.standard_config(), self.file_path)
            command = "sed -i '%dc %s' %s" % (self.line_num, self.standard_config(), self.file_path)
        elif self.status == 0:
            command = "echo %s >> %s" % (self.standard_config(), self.file_path)
        else:
            return
        print(execute(command))
        self.validate()


def escape(s=""):
    s = s.replace(".", "\\.").replace("*", "\\*")
    arr = re.split(" +", s)
    result = ""
    for i in range(len(arr) - 1):
        result += arr[i] + " +"
    result += arr[len(arr) - 1]
    return result


def display_colorful(specs, newline_at_end=True):
    for spec in specs:
        pad = padding(spec.desc)
        if spec.status == -2:
            print("%s [%s]" % (pad, red("文件不存在")))
        elif spec.status == -1:
            print("%s [%s]" % (pad, red("配置错误, 期望'%s', 实际'%s'" % (spec.exp_val, spec.act_val))))
        elif spec.status == 0:
            print("%s [%s]" % (pad, yellow("未配置")))
        elif spec.status == 1:
            print("%s [%s]" % (pad, green("配置正确")))
    if newline_at_end:
        print("")


def modify_optional(specs):
    for spec in specs:
        if spec.status == -1 or spec.status == 0:
            display_colorful([spec], False)
            if promised("是否修复 ? "):
                spec.modify()
