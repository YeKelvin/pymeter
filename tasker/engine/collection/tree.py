#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : hash_tree
# @Time    : 2020/2/24 14:54
# @Author  : Kelvin.Ye
from typing import Dict

from tasker.common.exceptions import UnsupportedOperationException
from tasker.engine.collection.traverser import ConvertToString
from tasker.engine.collection.traverser import TreeSearcher
from tasker.utils.log_util import get_logger


log = get_logger(__name__)


class HashTree(dict):

    def __init__(self, _dict: Dict[object, 'HashTree'] = None, key: object = None):
        super().__init__()
        # self.__data: Dict[object, 'HashTree'] = hash_tree if hash_tree is not None else {}
        self._data: Dict[object, 'HashTree'] = _dict or {}

        if key:
            self._data[key] = HashTree()

    def put(self, key: object, value: 'HashTree') -> 'HashTree':
        """添加key和subtree
        """
        previous = self.get_subtree(key)
        self.add_key_and_subtree(key, value)
        return previous

    def put_all(self, _dict: Dict[object, 'HashTree']):
        """添加hasttree
        """
        if isinstance(_dict, HashTree):
            self.add_newtree(_dict)
        else:
            raise UnsupportedOperationException('can only putAll other HashTree objects')

    def add_key(self, key: object) -> 'HashTree':
        """
        Adds an key into the HashTree at the current level.
        If a HashTree exists for the key already, no new tree will be added

        @param key key to be added to HashTree
        @return newly generated tree, if no tree was found for the given key;
                existing key otherwise
        """
        if not self.contains(key):
            new_tree = HashTree()
            self._data[key] = new_tree
            return new_tree

        return self.get_subtree(key)

    def add_key_and_subtree(self, key: object, subtree: 'HashTree') -> None:
        """
        Adds a key as a node at the current level and then adds the given
        HashTree to that new node.

        @param key     key to create in this tree
        @param subTree sub tree to add to the node created for the first argument.
        """
        self.add_key(key).add_newtree(subtree)

    def add_newtree(self, newtree: 'HashTree') -> None:
        """
        Adds all the nodes and branches of the given tree to this tree.
        Is like merging two trees. Duplicates are ignored.

        @param newTree the tree to be added
        """
        for item in newtree.list():
            self.add_key(item).add_newtree(newtree.get_subtree(item))

    def add_keys(self, keys: list) -> None:
        """
        Adds all the given objects as nodes at the current level.

        @param keys Array of Keys to be added to HashTree.
        """
        for key in keys:
            self.add_key(key)

    def add_key_and_subkey(self, key: object, subkey: object) -> 'HashTree':
        """添加key，并在第一个key下再继续添加key
        Adds a key and it's values in the HashTree.
        The first argument becomes a node at the current level,
        and adds all the values in the array to the new node.

        @param key    key to be added
        @param values array of objects to be added as keys in the secondary node
        """
        return self.add_key(key).add_key(subkey)

    def add_key_and_subkeys(self, key: object, subkeys: list) -> None:
        """添加key，并在第一个key下再继续添加keys列表
        Adds a key as a node at the current level and then adds all the objects in the second argument as nodes of the new node.

        @param key    key to be added
        @param values Collection of objects to be added as keys in the secondary node
        """
        self.add_key(key).add_keys(subkeys)

    def add_key_by_treepath(self, treepath: list, key: object) -> 'HashTree':
        """在treepath末尾添加key
        Adds a series of nodes into the HashTree using the given path.
        The first argument is a List that represents a path to a specific node in the tree.
        If the path doesn't already exist, it is created (the objects are added along the way).
        At the path, the object in the second argument is added as a node.

        @param treePath a list of objects representing a path
        @param value    Object to add as a node to bottom-most node
        @return HashTree for which <code>value</code> is the key
        """
        tree = self._add_treepath(treepath)
        return tree.add_key(key)

    def add_keys_by_treepath(self, treepath: list, keys: list) -> None:
        """在treepath末尾添加keys列表
        Adds a series of nodes into the HashTree using the given path.
        The first argument is a SortedSet that represents a path to a specific node in the tree.
        If the path doesn't already exist, it is created (the objects are added along the way).
        At the path, all the objects in the second argument are added as nodes.

        @param treePath a SortedSet of objects representing a path
        @param values   Collection of values to be added as keys to bottom-most node
        """
        tree = self._add_treepath(treepath)
        tree.add_keys(keys)

    def _add_treepath(self, treepath: list) -> 'HashTree':
        """添加 treepath（不存在时添加）
        """
        tree = self
        for item in treepath:
            tree = tree.add_key(item)
        return tree

    def get_subtree(self, node: object) -> 'HashTree':
        """返回key的hashtree，这个hashtree其实就是节点下的子节点
        """
        return self._data.get(node)

    def index(self, index) -> 'HashTree':
        """根据下标返回对应 node的 hashtree
        """
        return self.get_subtree(self.list()[index])

    def clear(self) -> None:
        """清空 hashtree
        """
        self._data.clear()

    def values(self):
        """返回当前 hashtree下的所有 subtree列表
        """
        return self._data.values()

    def contains(self, node: object) -> bool:
        """判断是否存在 node
        """
        return node in self._data

    def list(self) -> list:
        """返回当前 hashtree下 node的列表
        """
        return list(self._data.keys())

    def search(self, node: object) -> "HashTree":
        """在当前 hashtree下遍历搜索（深度优先） node
        """
        result = self.get_subtree(node)
        if result:
            return result
        searcher = TreeSearcher(node)
        try:
            self.traverse(searcher)
        except RuntimeError as e:
            if not str(e) == TreeSearcher.FOUND:
                raise e
        return searcher.result

    def traverse(self, visitor) -> None:
        """hashtree遍历（深度优先）
        """
        for node in self.list():
            visitor.add_node(node, self.get_subtree(node))
            self.get_subtree(node).__traverse_into(visitor)

    def __traverse_into(self, visitor) -> None:
        """hashtree遍历回调
        """
        if not self.list():
            visitor.process_path()
        else:
            for node in self.list():
                subtree = self.get_subtree(node)
                visitor.add_node(node, subtree)
                subtree.__traverse_into(visitor)

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

    def __init__(self, node: object = None, hash_tree: 'ListedHashTree' = None):
        super().__init__(node, hash_tree)
        self.order = []

    def add_node(self, node: object) -> 'ListedHashTree':
        if not self.contains(node):
            new_tree = ListedHashTree()
            self._data[node] = new_tree
            self.order.append(node)
            return new_tree
        return self.get_subtree(node)

    def clear(self):
        super().clear()
        self.order.clear()

    def list(self) -> list:
        return self.order
