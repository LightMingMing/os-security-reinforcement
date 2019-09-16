# -*- coding: UTF-8 -*-
"""
控制台相关
Author: 赵明明
"""


def promised(msg="?", color=1):
    """
    向用户发起询问, 获取许可
    :param msg: 消息
    :param color: 终端显示的颜色, 0系统颜色, 1绿色, 2黄色, 3红色, 其它系统颜色
    :return: 用户输入YES'、'yes'、'Y'或'y'返回True; 输入'NOT'、'not'、'N'或'n'返回False
    """
    promise = ""
    if not msg.endswith("?") and not msg.endswith("? "):
        # 避免忘记加问好
        msg += "? "
    if color == 1:
        msg = green(msg)
    elif color == 2:
        msg = yellow(msg)
    elif color == 3:
        msg = red(msg)
    try:
        while promise not in ['YES', 'yes', 'Y', 'y', 'NOT', 'not', 'N', 'n']:
            # TODO 这里Python2和Python3有些不一样
            # Python2 raw_input(msg)
            # Python3 input(msg)
            promise = str(raw_input(msg))
    except KeyboardInterrupt:
        print("")
        exit(1)
    if promise in ['yes', 'y']:
        return True
    else:
        return False


def padding(msg, total_len=80, padding_char='.'):
    """定长补白后的消息"""
    if not msg.endswith(" "):
        msg += " "
    if len(padding_char) != 0:
        padding_char = '.'
    for i in range(len_padding(total_len, msg)):
        msg += padding_char
    return msg


def num_ascii(s):
    """计算字符串中, ascii字符的个数"""
    n = 0
    for c in range(len(s)):
        if ord(s[c]) < 128:
            n += 1
    return n


def len_padding(total_len, prefix):
    """计算补白长度, 用于美化控制台输出"""
    if len('中') == 1:
        return total_len - 2 * len(prefix) + num_ascii(prefix)  # python3
    else:
        return total_len - (2 * len(prefix) + num_ascii(prefix)) / 3  # python2


def red(s):
    return "\033[31m" + s + "\033[0m"


def yellow(s):
    return "\033[33m" + s + "\033[0m"


def green(s):
    return "\033[34m" + s + "\033[0m"


def info(msg):
    print(green(msg))
