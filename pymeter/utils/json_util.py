#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : json_util.py
# @Time    : 2020/2/21 11:14
# @Author  : Kelvin.Ye
import random
import re

import orjson
from jsonpath import jsonpath
from orjson import JSONDecodeError


DECODE_ERROR_PATTERN = re.compile(r'line [\d]+ column [\d]+ \(char [\d]+\)$')
NUMBER_PATTERN = re.compile(r'[\d]+')


class JsonpathExtractException(Exception):
    ...


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
        if match := DECODE_ERROR_PATTERN.search(e.args[0]):
            position_msg = match.group()
            position = NUMBER_PATTERN.findall(position_msg)
            line = int(position[0])
            ch = int(position[2])
            lines = val.split('\n')
            if line == 1:  # 第一行报错，直接用 char 定位
                if ch > 10:
                    char_count = len(val)
                    msg = val[ch - 10: ch+10] if char_count > ch + 10 else val[ch - 10]
                else:
                    msg = val
            else:
                line_count = len(lines)
                if line_count > line:
                    msg = ''.join(lines[line - 2: line + 1])
                else:
                    msg = ''.join(lines[line - 2:])
            e.args = (f'{e.args[0]}\n--->{msg}',)
        raise e


def json_path(val, expressions, choice=False, throw=False):
    results = jsonpath(from_json(val), expressions)

    # jsonpath 没有匹配时会返回 False
    if not results:
        if throw:
            raise JsonpathExtractException
        return

    if len(results) == 1:
        result = results[0]
        if isinstance(result, list):
            return random.choice(result) if choice else result
        else:
            return result

    return random.choice(results) if choice else results
