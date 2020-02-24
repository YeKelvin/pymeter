#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : hash_tree
# @Time    : 2020/2/24 14:54
# @Author  : Kelvin.Ye
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class HashTree(dict):
    def __init__(self, key: object = None):
        super().__init__()
        self.__data: {object, HashTree} = {}
        if key:
            self.__data[key] = HashTree()

    def put(self, key: object, value: {}):
        self.__data[key] = value

    def put_all(self, _dict: {}):
        self.__data.update(_dict)

    def get(self, key: object) -> {}:
        return self.__data.get(key, None)

    def clear(self):
        self.__data.clear()

    def values(self):
        return self.__data.values()

    def contains(self, key: object):
        return key in self.__data


class ListedHashTree(HashTree):
    pass
