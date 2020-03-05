#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : hash_tree
# @Time    : 2020/2/24 14:54
# @Author  : Kelvin.Ye
from sendanywhere.engine.collection.traverser import ConvertToString, TreeSearcher
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class HashTree(dict):
    def __init__(self, node: object = None, hash_tree: 'HashTree' = None):
        super().__init__()
        self.__data: {object, 'HashTree'} = hash_tree if hash_tree is not None else {}

        if node:
            self.__data[node] = HashTree()

    # def put(self, node: object, hash_tree: "HashTree" = None) -> None:
    #     """添加 node和 hashtree，node存在时则替换 hashtree
    #     """
    #     self.__data[node] = hash_tree if hash_tree is not None else HashTree()
    #
    # def put_all(self, node: object, collections: ["HashTree" or object]) -> None:
    #     """根据 node遍历添加 collections中的节点
    #     """
    #     hash_tree = self.get(node) if self.contains(node) else HashTree()
    #
    #     for item in collections:
    #         if isinstance(item, HashTree):
    #             hash_tree.merge(item)
    #         elif isinstance(item, object):
    #             hash_tree.put(item)
    #
    #     self.put(node, hash_tree)

    def put(self, node: object, hashtree: 'HashTree') -> 'HashTree':
        log.info(f'node={node}, hashtree={hashtree}')
        previous = self.get(node)
        self.add_node_and_subtree(node, hashtree)
        return previous

    # --------------------------------------------------------------------------

    def add_node(self, node: object) -> 'HashTree':
        if not self.contains(node):
            new_tree = HashTree()
            self.__data[node] = new_tree
            return new_tree
        return self.get_subtree(node)

    def add_node_and_subtree(self, node: object, subtree: 'HashTree') -> None:
        self.add_node(node).add_newtree(subtree)

    def add_newtree(self, newtree: 'HashTree') -> None:
        for node in newtree.list():
            self.add_node(node).add_newtree(newtree.get(node))

    def add_list(self, nodes: list) -> None:
        for node in nodes:
            self.add_node(node)

    def add_node_and_subnode(self, node: object, subnode: object) -> 'HashTree':
        return self.add_node(node).add_node(subnode)

    def add_node_and_sublist(self, node: object, subnodes: list) -> None:
        self.add_node(node).add_list(subnodes)

    def add_node_by_treepath(self, treepath: list, node: object) -> 'HashTree':
        tree = self.__add_treepath(treepath)
        return tree.add_key(node)

    def add_nodes_by_treepath(self, treepath: list, nodes: list) -> None:
        tree = self.__add_treepath(treepath)
        tree.add_list(nodes)

    def __add_treepath(self, treepath: list):
        tree = self
        for node in treepath:
            tree = tree.add_key(node)
        return tree

    # --------------------------------------------------------------------------

    def get_subtree(self, node: object) -> 'HashTree':
        """获取 node的 hashtree
        """
        return self.__data.get(node)

    # def merge(self, hash_tree: "HashTree"):
    #     """合并 hashtree
    #     """
    #     node_list = hash_tree.list()
    #     for node in node_list:
    #         self.put(node, hash_tree.get(node))

    def index(self, index) -> 'HashTree':
        return self.__data.get(self.list()[index])

    def clear(self) -> None:
        """清空 hashtree
        """
        self.__data.clear()

    def values(self):
        return self.__data.values()

    def contains(self, node: object) -> bool:
        """判断是否存在 node
        """
        return node in self.__data

    def list(self) -> list:
        """返回 hashtree下 node的列表
        """
        return list(self.__data.keys())

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
        """HashTree遍历（深度优先）
        """
        for node in self.list():
            visitor.add_node(node, self.get_subtree(node))
            self.get_subtree(node).__traverse_into(visitor)

    def __traverse_into(self, visitor) -> None:
        """HashTree遍历回调
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

    def put(self, node: object, hash_tree: 'ListedHashTree' = None):
        if not self.contains(node):
            self.order.append(node)
        super().put(node, hash_tree if hash_tree is not None else ListedHashTree())

    def clear(self):
        super().clear()
        self.order.clear()

    def list(self) -> list:
        return self.order
