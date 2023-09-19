#!/usr/bin python3
# @File    : advanced.py
# @Time    : 2021-09-08 11:06:50
# @Author  : Kelvin.Ye
import orjson


class JsonDict(dict):

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __delattr__(self, item):
        self.__delitem__(item)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return orjson.dumps(self).decode('utf8')


class JsonList(list):

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return orjson.dumps(self).decode('utf8')


def transform(value: list or dict):
    """将 Dict 、List 或 List[dict] 转换为 JsonDict / JsonList"""
    if isinstance(value, list):
        attrs = JsonList()
        for item in value:
            if isinstance(item, dict | list):
                attrs.append(transform(item))
            else:
                attrs.append(item)
        return attrs
    elif isinstance(value, dict):
        attrs = JsonDict()
        for key, val in value.items():
            attrs[key] = transform(val) if isinstance(val, dict | list) else val
        return attrs
    else:
        return value
