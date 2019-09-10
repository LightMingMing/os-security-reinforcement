# -*- coding: UTF-8 -*-
"""
系统配置封装为对象
Author: 赵明明
"""

import os
import re

from color import red, yellow, green


class Prop(object):
    """属性"""

    def __init__(self, desc, file_path, key, exp_val, op=" ", pattern_split=" +", num_split=2):
        self._desc = desc
        self._file_path = file_path
        self._key = key
        self._exp_val = exp_val
        self._rel_val = None
        self._status = 0
        self._op = op
        # self._pattern_prefix = escape(self._key) + pattern_split
        self._pattern_prefix = re.compile(escape(self._key) + pattern_split)
        # self._pattern_split = pattern_split
        self._pattern_split = re.compile(pattern_split)
        self._num_split = num_split
        self._num_line = 0
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
    def rel_val(self):
        return self._rel_val

    @property
    def status(self):
        return self._status

    @property
    def num_line(self):
        return self._num_line

    def standard_config(self):
        return self._key + self._op + self._exp_val

    def validate(self):
        try:
            f = open(self._file_path, "rb")
            context = f.read()
            f.close()
            self._num_line = 0
            for line in context.splitlines():
                self._num_line += 1
                if self._pattern_prefix.match(str(line)):
                    arr = self._pattern_split.split(str(line), self._num_split)
                    self._rel_val = arr[self._num_split - 1]
                    if self._exp_val == self._rel_val:
                        # 期望配置
                        self._status = 1
                    else:
                        # 非期望配置
                        self._status = -1
                    return
            # 未配置
            self._num_line = 0
            self._status = 0
        except IOError:
            # 文件操作异常
            self._num_line = -1
            self._status = -2

    def modify(self):
        if self.status == -1:
            # TODO 暂时伪修复
            command = "sed -n '%dc %s' %s" % (self.num_line, self.standard_config(), self.file_path)
            # command = "sed -i '%dc %s' %s" % (self.num_line, self.standard_config(), self.file_path)
        elif self.status == 0:
            command = "echo %s >> %s" % (self.standard_config(), self.file_path)
        else:
            return
        print(command)
        f = os.popen(command)
        print(f.read())
        f.close()
        self.validate()


def escape(s=""):
    s = s.replace(".", "\\.").replace("*", "\\*")
    arr = re.split(" +", s)
    result = ""
    for i in range(len(arr) - 1):
        result += arr[i] + " +"
    result += arr[len(arr) - 1]
    return result


def num_ascii(s):
    n = 0
    for c in range(len(s)):
        if ord(s[c]) < 128:
            n += 1
    return n


def len_padding(total_len, prefix):
    if len('中') == 1:
        return total_len - 2 * len(prefix) + num_ascii(prefix)  # python3
    else:
        return total_len - (2 * len(prefix) + num_ascii(prefix)) / 3  # python2


def padding(total_len, prefix):
    s = ""
    for i in range(len_padding(total_len, prefix)):
        s += "."
    return s


def show_colorful(props, flags=True):
    for prop in props:
        pad = padding(80, prop.desc)
        if prop.status == -2:
            print("%s %s [%s]" % (prop.desc, pad, red("文件不存在")))
        elif prop.status == -1:
            print("%s %s [%s]" % (prop.desc, pad, red("配置错误, 期望'%s', 实际'%s'" % (prop.exp_val, prop.rel_val))))
        elif prop.status == 0:
            print("%s %s [%s]" % (prop.desc, pad, yellow("未配置")))
        elif prop.status == 1:
            print("%s %s [%s]" % (prop.desc, pad, green("配置正确")))
    if flags:
        print("")


def modify_optional(props):
    for prop in props:
        if prop.status == -1 or prop.status == 0:
            show_colorful([prop], False)
            promise = ""
            try:
                while promise not in ['yes', 'y', 'not', 'n']:
                    # TODO Python2(raw_input) Python3(input)
                    promise = str(raw_input(green("是否修复 ? ")))
            except KeyboardInterrupt:
                print("")
                exit(1)
            if promise in ['yes', 'y']:
                prop.modify()
