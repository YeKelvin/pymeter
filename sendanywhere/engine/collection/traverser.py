#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : traverser
# @Time    : 2020/2/25 15:06
# @Author  : Kelvin.Ye
from queue import LifoQueue

from sendanywhere.assertions.assertion import Assertion
from sendanywhere.configs.config import ConfigElement
from sendanywhere.controls.controller import Controller
from sendanywhere.controls.loop_controller import LoopController
from sendanywhere.coroutines.package import SamplePackage
from sendanywhere.engine.listener import SampleListener
from sendanywhere.processors.post import PostProcessor
from sendanywhere.processors.pre import PreProcessor
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class HashTreeTraverser:

    def add_node(self, node, subtree) -> None:
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

    def add_node(self, node, subtree) -> None:
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

    def add_node(self, node, subtree) -> None:
        self.depth += 1
        self.string.append('\n')
        self.string.append(self.get_spaces())
        self.string.append(str(node))
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

    def get_subtree(self, node: object):
        return self.subtrees.get(node)

    def add_node(self, node, subtree) -> None:
        if isinstance(node, self.search_class):
            self.objects_of_class.append(node)
            from sendanywhere.engine.collection.tree import HashTree
            tree = HashTree()
            tree.put(node, subtree)
            self.subtrees[node] = tree

    def subtract_node(self) -> None:
        pass

    def process_path(self) -> None:
        pass


class GroupCompiler(HashTreeTraverser):
    def __init__(self, group_level_elements: list, sample_controller: LoopController):
        self.group_level_elements = group_level_elements
        self.sample_controller = sample_controller
        self.sampler_package_saver: {Sampler, SamplePackage} = {}

    def add_node(self, node, subtree) -> None:
        if isinstance(node, Sampler):
            self.save_sampler_subnodes(node, subtree)

    def subtract_node(self) -> None:
        pass

    def process_path(self) -> None:
        pass

    def save_sampler_subnodes(self, node, subtree):
        sample_package = SamplePackage()
        sample_package.add(subtree.list())  # 储存 Sampler下的子节点
        sample_package.add(self.group_level_elements)  # 把 group层的非 group节点添加至 Sampler节点下
        self.sampler_package_saver[node] = sample_package

    def get_sample_package(self, sampler: Sampler) -> SamplePackage:
        return self.sampler_package_saver.get(sampler)
