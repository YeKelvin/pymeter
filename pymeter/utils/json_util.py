#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : json_util.py
# @Time    : 2020/2/21 11:14
# @Author  : Kelvin.Ye
import random
import re
from collections.abc import Sequence

import orjson
from jsonpath import jsonpath
from orjson import JSONDecodeError


DECODE_ERROR_PATTERN = re.compile('line [\d]+ column [\d]+ \(char [\d]+\)$')
NUMBER_PATTERN = re.compile('[\d]+')


def to_json(obj: dict or list) -> str:
    """序列化"""
    try:
        return orjson.dumps(obj).decode('utf8')
    except TypeError as e:
        e.args = e.args + (f'obj:[ {obj} ]',)
        raise e


def from_json(val):
    """反序列化"""
    try:
        return orjson.loads(val)
    except JSONDecodeError as e:
        match = DECODE_ERROR_PATTERN.search(e.args[0])
        if match:
            position_msg = match.group()
            position = NUMBER_PATTERN.findall(position_msg)
            line = int(position[0])
            # column = int(position[1])
            ch = int(position[2])
            lines = val.split('\n')
            line_count = len(lines)
            char_count = len(val)
            if line == 1:  # 第一行报错，直接用 char 定位
                if char_count > ch + 10:
                    if ch > 10:
                        msg = val[ch -10: ch+10]
                    else:
                        msg = val
                else:
                    if ch > 10:
                        msg = val[ch -10]
                    else:
                        msg = val
            else:
                if line_count > line:
                    msg = ''.join(lines[line -2: line + 1])
                else:
                    msg = ''.join(lines[line -2:])
            e.args = (f'{e.args[0]}\n--->{msg}',)
            raise e
        else:
            raise e


def json_path(val, xpath, choice=False, index=None):
    results = jsonpath(from_json(val), xpath)
    if len(results) == 1:
        result = results[0]
        if choice and isinstance(result, Sequence):
            return random.choice(result)
        elif index is not None and isinstance(result, Sequence):
            return result[index]
        else:
            return result
    if choice:
        return random.choice(results)
    return results
