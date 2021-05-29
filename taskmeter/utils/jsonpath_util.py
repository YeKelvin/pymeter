#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : jsonpath_util.py
# @Time    : 2020/2/21 11:15
# @Author  : Kelvin.Ye
from jsonpath import jsonpath

from taskmeter.utils.json_util import from_json


def extract_json(json_text: str, json_path: str):
    """根据 JsonPath提取字段值
    """
    result_list = jsonpath(from_json(json_text), json_path)
    if len(result_list) == 1:
        return result_list[0]
    return result_list
