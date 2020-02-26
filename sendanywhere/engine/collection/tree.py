#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : hash_tree
# @Time    : 2020/2/24 14:54
# @Author  : Kelvin.Ye
import sys

from sendanywhere.engine.collection.traverser import ConvertToString, TreeSearcher
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

    def search(self, key: object) -> "HashTree":
        result = self.get(key)
        if result:
            return result
        searcher = TreeSearcher(key)
        try:
            self.traverse(searcher)
        except RuntimeError as e:
            if not str(e) == TreeSearcher.FOUND:
                raise e
        return searcher.result

    def traverse(self, visitor):
        """HashTree遍历（深度优先）
        """
        for item in self.list():
            visitor.add_node(item, self.get(item))
            self.get(item).__traverse_into(visitor)

    def __traverse_into(self, visitor):
        """HashTree遍历回调
        """
        if not self.list():
            visitor.process_path()
        else:
            for item in self.list():
                treeItem = self.get(item)
                visitor.add_node(item, treeItem)
                treeItem.__traverse_into(visitor)

        visitor.subtract_node()

    def __str__(self):
        converter = ConvertToString()
        self.traverse(converter)
        return str(converter)

    def __repr__(self):
        return self.__str__()


class ListedHashTree(HashTree):
    """
    ListedHashTree是 HashTree的另一种实现。
    在 ListedHashTree中，保留了添加值的顺序。
    """
    def __init__(self, key: object = None, value: "ListedHashTree" = None):
        super().__init__(key, value)
        self.order = []

    def put(self, key: object, value: "ListedHashTree"):
        if not self.contains(key):
            self.order.append(key)
        super().put(key, value)

    def clear(self):
        super().clear()
        self.order.clear()

    def list(self) -> list:
        return self.order
