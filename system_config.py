# -*- coding: UTF-8 -*-
"""
系统配置封装为对象
Author: 赵明明
"""

import re


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
        self._pattern_prefix = escape(self._key) + pattern_split
        self._pattern_split = pattern_split
        self._num_split = num_split
        self.__validate()

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

    def __validate(self):
        try:
            f = open(self._file_path, "rb")
            context = f.read()
            f.close()
            lines = context.split("\n")
            for line in lines:
                if re.match(self._pattern_prefix, line):
                    arr = re.split(self._pattern_split, line, self._num_split)
                    self._rel_val = arr[self._num_split - 1]
                    if self._exp_val == self._rel_val:
                        self._status = 1
                    else:
                        self._status = -1
                    return
            # 未配置
            self._status = 0
        except IOError:
            # 文件操作异常
            self._status = -2


def escape(s=""):
    s = s.replace(".", "\\.").replace("*", "\\*")
    arr = re.split(" +", s)
    result = ""
    for i in range(len(arr) - 1):
        result += arr[i] + " +"
    result += arr[len(arr) - 1]
    return result
