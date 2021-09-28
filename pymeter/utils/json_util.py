#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : json_util.py
# @Time    : 2020/2/21 11:14
# @Author  : Kelvin.Ye
import random
from collections.abc import Sequence

import orjson
from jsonpath import jsonpath
from orjson import JSONDecodeError


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
        e.args = e.args + (f'value:[ {val} ]',)
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
