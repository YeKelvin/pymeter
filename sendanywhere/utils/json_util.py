#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : json_util.py
# @Time    : 2020/2/21 11:14
# @Author  : Kelvin.Ye
import orjson


def to_json(obj: dict or list) -> str:
    """序列化
    """
    return orjson.dumps(obj)


def from_json(json_text: str) -> dict or list:
    """反序列化
    """
    return orjson.loads(json_text)
