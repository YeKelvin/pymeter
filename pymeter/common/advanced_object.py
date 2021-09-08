#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : advanced_object.py
# @Time    : 2021-09-08 11:06:50
# @Author  : Kelvin.Ye


class ItemDict(dict):

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __delattr__(self, item):
        self.__delitem__(item)


def transform(value: list or dict):
    """将 Dict 或 List[dict] 转换为 ItemDict """
    if isinstance(value, list):
        attrs = []
        for item in value:
            if isinstance(item, dict) or isinstance(item, list):
                attrs.append(transform(item))
            else:
                attrs.append(item)
        return attrs
    elif isinstance(value, dict):
        attrs = {}
        for key, val in value.items():
            if isinstance(val, dict) or isinstance(val, list):
                attrs[key] = transform(val)
            else:
                attrs[key] = val
        return ItemDict(attrs)
    else:
        return value
