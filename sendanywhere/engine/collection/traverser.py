#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : traverser
# @Time    : 2020/2/25 15:06
# @Author  : Kelvin.Ye
from queue import LifoQueue

from sendanywhere.samplers.sampler import Sampler
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class HashTreeTraverser:

    def add_node(self, key, subtree) -> None:
        """加节点时的处理
        """
        raise NotImplementedError

    def subtract_node(self) -> None:
        """减节点时的处理（递归回溯）
        """
        raise NotImplementedError

    def process_path(self) -> None:
        """到达树底部时的处理
        """
        raise NotImplementedError


class TreeSearcher(HashTreeTraverser):
    FOUND = 'found'

    def __init__(self, target: object):
        self.target = target
        self.result = None

    def add_node(self, key, subtree) -> None:
        result = subtree.get(self.target)
        if result:
            raise RuntimeError(self.FOUND)

    def subtract_node(self) -> None:
        pass

    def process_path(self) -> None:
        pass


class ConvertToString(HashTreeTraverser):
    def __init__(self):
        self.string = ['{']
        self.spaces = []
        self.depth = 0

    def add_node(self, key, subtree) -> None:
        self.depth += 1
        self.string.append('\n')
        self.string.append(self.get_spaces())
        self.string.append(str(key))
        self.string.append(' {')

    def subtract_node(self) -> None:
        self.string.append('\n')
        self.string.append(self.get_spaces())
        self.string.append('}')
        self.depth -= 1

    def process_path(self) -> None:
        pass

    def get_spaces(self):
        if len(self.spaces) < self.depth * 2:
            while len(self.spaces) < self.depth * 2:
                self.spaces.append('  ')
        elif len(self.spaces) > self.depth * 2:
            self.spaces = self.spaces[0:self.depth * 2]
        return ''.join(self.spaces)

    def __str__(self):
        self.string.append('\n}')
        return ''.join(self.string)

    def __repr__(self):
        return self.__str__()


class SearchByClass(HashTreeTraverser):
    def __init__(self, search_class: type):
        self.objects_of_class = []
        self.subtrees = {}
        self.search_class = search_class

    def get_search_result(self) -> list:
        return self.objects_of_class

    def get_subtree(self, key: object):
        return self.subtrees.get(key)

    def add_node(self, key, subtree) -> None:
        if isinstance(key, self.search_class):
            self.objects_of_class.append(key)
            from sendanywhere.engine.collection.tree import HashTree
            tree = HashTree()
            tree.put(key, subtree)
            self.subtrees[key] = tree

    def subtract_node(self) -> None:
        pass

    def process_path(self) -> None:
        pass


class TestCompiler(HashTreeTraverser):
    def __init__(self, tree):
        self.tree = tree
        self.stack = LifoQueue()
        self.sampler_config_map = {}

    def add_node(self, key, subtree) -> None:
        self.stack.put(key)

    def subtract_node(self) -> None:
        log.debug(f'Subtracting node, stack size = {self.stack.qsize()}')
        child = self.stack.get()

        if isinstance(child, Sampler):
            self.save_sampler_configs(child)

    def process_path(self) -> None:
        pass

    def save_sampler_configs(self):
        configs = []
        controllers = []
        preProcessors = []
        listeners = []
        postProcessors = []
        assertions = []
        for node in range(self.stack.qsize(), -1, -1):
            pass
