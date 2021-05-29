#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : time_util
# @Time    : 2020/3/9 15:20
# @Author  : Kelvin.Ye
import time
from datetime import datetime


STRFTIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def strftime(time_format: str = STRFTIME_FORMAT) -> str:
    """获取当前时间并格式化为时间字符串

    Args:
        time_format:    时间格式

    Returns:            str

    """
    return datetime.now().strftime(time_format)


def timestamp_as_s() -> int:
    """获取秒级时间戳
    """
    return int(time.time())


def timestamp_as_ms() -> int:
    """获取毫秒级时间戳
    """
    return int(time.time() * 1000)


def timestamp_as_micro_s() -> int:
    """获取微秒级时间戳
    """
    return int(round(time.time() * 1000000))


def timestamp_convert_to_strftime(format: str = STRFTIME_FORMAT, timestamp: float = 0):
    """时间戳转时间字符串

    Args:
        format:     时间格式
        timestamp:  时间戳

    Returns:        float

    """
    return time.strftime(format, time.localtime(timestamp))


def strftime_convert_to_timestamp_as_ms(strftime: str, format: str = STRFTIME_FORMAT):
    """时间字符串转毫秒级时间戳

    Args:
        strftime:   时间字符串
        format:     时间格式

    Returns:        float

    """
    return int(time.mktime(time.strptime(strftime, format)) * 1000)


def change_strftime_format(strftime: str, old_format: str, new_format: str = STRFTIME_FORMAT):
    """更改时间字符串的格式

    Args:
        strftime:   时间字符串
        old_format: 旧格式
        new_format: 新格式

    Returns:        str

    """
    return datetime.strptime(strftime, old_format).strftime(new_format)


def seconds_convert_to_h_m_s(seconds: int) -> str:
    """秒数转换为时分秒
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return '%02dh:%02dm:%02ds' % (h, m, s)
