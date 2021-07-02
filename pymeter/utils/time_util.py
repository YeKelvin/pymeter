#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : time_util
# @Time    : 2020/3/9 15:20
# @Author  : Kelvin.Ye
import time
from datetime import datetime


DEFAULE_STRFTIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def strftime_now(fmt: str = DEFAULE_STRFTIME_FORMAT) -> str:
    """获取当前时间并格式化为时间字符串"""
    return datetime.now().strftime(fmt)


def timestamp_now() -> int:
    """获取时间戳"""
    return time.time()


def timestamp_to_strftime(timestamp: float, fmt: str = DEFAULE_STRFTIME_FORMAT):
    """时间戳转时间字符串

    Args:
        timestamp:  时间戳
        fmt:        时间格式

    """
    return datetime.fromtimestamp(timestamp).strftime(fmt)


def strftime_to_timestamp(strftime: str, fmt: str = DEFAULE_STRFTIME_FORMAT) -> float:
    """时间字符串转毫秒级时间戳

    Args:
        strftime:   时间字符串
        fmt:        时间格式

    """
    return int(time.mktime(time.strptime(strftime, fmt)) * 1000)


def change_strftime_format(strftime: str, old_fmt: str, new_fmt: str = DEFAULE_STRFTIME_FORMAT) -> str:
    """更改时间字符串的格式

    Args:
        strftime:   时间字符串
        old_fmt:    旧格式
        new_fmt:    新格式

    """
    return datetime.strptime(strftime, old_fmt).strftime(new_fmt)


def seconds_convert_to_h_m_s(seconds: int) -> str:
    """秒数转换为时分秒
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return '%02dh:%02dm:%02ds' % (h, m, s)
