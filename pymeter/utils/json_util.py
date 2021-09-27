#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : json_util.py
# @Time    : 2020/2/21 11:14
# @Author  : Kelvin.Ye
import random
from collections.abc import Iterable

import orjson
from jsonpath import jsonpath


def to_json(obj: dict or list) -> str:
    """序列化"""
    return orjson.dumps(obj).decode('utf8')


def from_json(json: str) -> any:
    """反序列化"""
    return orjson.loads(json)


def json_path(val, xpath, choice=False, index=None):
    results = jsonpath(from_json(val), xpath)
    if len(results) == 1:
        result = results[0]
        if choice and isinstance(result, Iterable):
            return random.choice(result)
        elif index is not None and isinstance(result, Iterable):
            return result[index]
        else:
            return result
    if choice:
        return random.choice(results)
    return results
