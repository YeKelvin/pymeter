#!/usr/bin python3
# @File    : hashtree
# @Time    : 2020/2/24 14:54
# @Author  : Kelvin.Ye
from pymeter.engines.traverser import ConvertToString
from pymeter.engines.traverser import TreeSearcher


"""
    (key):  (value)
root_node: hashtree
            |
            |   (key):  (value)
            |-worker1: hashtree
            |           |
            |           |    (key):  (value)
            |           |-sampler1: hashtree
            |           |
            |           |    (key):  (value)
            |           |-sampler2: None
            |
            |   (key):  (value)
            |-worker2: hashtree
            |
            ...

"""


class HashTree:

    def __init__(self, hashtree: dict[object, 'HashTree'] = None, node: object = None):
        self.data: dict[object, 'HashTree'] = hashtree or {}

        if node:
            self.data[node] = HashTree()

    def put(self, key: object, value: 'HashTree') -> 'HashTree':
        """添加key和subtree"""
        prev = self.get(key)
        self.add_subtree(key, value)
        return prev

    def add_key(self, node: object) -> 'HashTree':
        """将key添加到当前级别的HashTree中，如果key已经存在，则不会添加新的HashTree。

        Args:
            node: 节点对象

        Returns:
            HashTree: 给定key的HashTree，如果没有则返回新的HashTree。
        """
        if not self.contains(node):
            new_tree = HashTree()
            self.data[node] = new_tree
            return new_tree

        return self.get(node)

    def add_subtree(self, node: object, subtree: 'HashTree') -> None:
        """public void add(Object key, HashTree subTree)

        添加一个键作为当前级别的节点，然后将给定的HashTree添加到该新节点。

        Args:
            node   : 节点对象
            subtree: 子树

        Returns:
            None
        """
        self.add_key(node).add_newtree(subtree)

    def add_newtree(self, newtree: 'HashTree') -> None:
        """public void add(HashTree newTree)

        将给定树的所有节点和分支添加到这个树上，就像合并两棵树一样。重复的部分被忽略。
        """
        for item in newtree.list():
            self.add_key(item).add_newtree(newtree.get(item))

    def add_keys(self, nodes: list) -> None:
        """public void add(Object[] keys)

        添加所有给定的对象作为当前级别的节点。
        """
        for node in nodes:
            self.add_key(node)

    def add_key_by_treepath(self, treepath: list, node: object) -> 'HashTree':
        """public HashTree add(Object[] treePath, Object value)

        使用给定的路径将一系列节点添加到HashTree中。
        第一个参数是一个SortedSet，表示通往树中特定节点的路径。
        如果该路径不存在，它就会被创建（对象是沿途添加的）。
        在路径上，第二个参数中的所有对象都被添加为节点。

        Args:
            treepath: 节点路径
            node    : 添加至treepath底部的节点列表

        Returns:
            HashTree: 给定node的HashTree
        """
        tree = self.add_treepath(treepath)
        return tree.add_key(node)

    def add_keys_by_treepath(self, treepath: list, nodes: list) -> None:
        """public void add(Object[] treePath, Object[] values)

        使用给定的路径将一系列节点添加到HashTree中。
        第一个参数是一个SortedSet，表示通往树中特定节点的路径。
        如果该路径不存在，它就会被创建（对象是沿途添加的）。
        在路径上，第二个参数中的所有对象都被添加为节点。

        Args:
            treepath: 节点路径
            nodes   : 添加至treepath底部的节点列表

        Returns:
            None
        """
        tree = self.add_treepath(treepath)
        tree.add_keys(nodes)

    def add_treepath(self, treepath: list) -> 'HashTree':
        """protected HashTree addTreePath(Collection<?> treePath)

        添加treepath，不存在时添加

        Args:
            treepath: 节点路径

        Returns:
            HashTree: 给定treepath最后一个节点的HashTree
        """
        tree = self
        for item in treepath:
            tree = tree.add_key(item)

        return tree

    def get_treepath(self, treepath: list) -> 'HashTree':
        """public HashTree getTree(Object[] treePath)

        通过在HashTree结构中一次一个键的递归，获取映射到数组中最后一个键的HashTree对象。

        Args:
            treepath: 节点路径

        Returns:
            HashTree: 给定treepath最后一个节点的HashTree
        """
        if not treepath:
            return self

        tree = self
        for node in treepath:
            tree = tree.get(node)
            if tree is None:
                return None

        return tree

    def get(self, key: object) -> 'HashTree':
        """获取给定key的hashtree（其实就是节点的children）"""
        return self.data.get(key)

    def index(self, index) -> 'HashTree':
        return self.get(self.list()[index])

    def clear(self) -> None:
        self.data.clear()

    def values(self):
        return self.data.values()

    def contains(self, node: object) -> bool:
        return node in self.data

    def list(self) -> list:
        return list(self.data.keys())

    def list_by_treepath(self, treepath: list):
        tree = self.get_treepath(treepath)
        return tree.list() if tree is not None else []

    def search(self, node: object) -> "HashTree":
        """搜索HashTree（深度优先）"""
        if result := self.get(node):
            return result

        searcher = TreeSearcher(node)
        try:
            self.traverse(searcher)
        except RuntimeError as e:
            if str(e) != TreeSearcher.FOUND:
                raise e

        return searcher.result

    def traverse(self, visitor) -> None:
        """遍历HashTree（深度优先）"""
        for node in self.list():
            visitor.add_node(node, self.get(node))
            self.get(node).traverse_into(visitor)

    def traverse_into(self, visitor) -> None:
        """遍历回调"""
        if not self.list():
            visitor.process_path()
        else:
            for node in self.list():
                subtree = self.get(node)
                visitor.add_node(node, subtree)
                subtree.traverse_into(visitor)

        visitor.subtract_node()

    def __str__(self):
        converter = ConvertToString()
        self.traverse(converter)
        return str(converter)

    def __repr__(self):
        return self.__str__()
