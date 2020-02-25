#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : hash_tree
# @Time    : 2020/2/24 14:54
# @Author  : Kelvin.Ye
import sys

from sendanywhere.engine.collection.traverser import ConvertToString
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class HashTree(dict):
    def __init__(self, key: object = None, value: "HashTree" = None):
        super().__init__()
        if value:
            self.__data: {object, "HashTree"} = value
        else:
            self.__data: {object, "HashTree"} = {}

        if key:
            self.__data[key] = HashTree()

    def put(self, key: object, value: "HashTree"):
        self.__data[key] = value

    def put_all(self, _dict: dict):
        self.__data.update(_dict)

    def get(self, key: object) -> "HashTree":
        return self.__data.get(key)

    def clear(self):
        self.__data.clear()

    def values(self):
        return self.__data.values()

    def contains(self, key: object):
        return key in self.__data

    def list(self) -> list:
        return list(self.__data.keys())

    def traverse(self, visitor):
        """HashTree遍历（深度优先）
        """
        for item in self.list():
            visitor.add_node(item, self.get(item))
            self.get(item).traverse_into(visitor)

    def traverse_into(self, visitor):
        """HashTree遍历回调
        """
        if not self.list():
            visitor.process_path()
        else:
            for item in self.list():
                treeItem = self.get(item)
                visitor.add_node(item, treeItem)
                treeItem.traverse_into(visitor)

        visitor.subtract_node()

    def __str__(self):
        converter = ConvertToString()
        self.traverse(converter)
        return str(converter)

    def __repr__(self):
        return self.__str__()


class ListedHashTree(HashTree):
    pass
