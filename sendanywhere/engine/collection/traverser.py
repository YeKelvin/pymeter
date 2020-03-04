#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : traverser
# @Time    : 2020/2/25 15:06
# @Author  : Kelvin.Ye
from sendanywhere.controls.controller import Controller
from sendanywhere.controls.generic_controller import GenericController
from sendanywhere.coroutines.package import SamplePackage
from sendanywhere.engine.listener import LoopIterationListener
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.testelement.test_element import TestElement
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
        self.string.append(self.__get_spaces())
        self.string.append(str(node))
        self.string.append(' {')

    def subtract_node(self) -> None:
        self.string.append('\n')
        self.string.append(self.__get_spaces())
        self.string.append('}')
        self.depth -= 1

    def process_path(self) -> None:
        pass

    def __get_spaces(self):
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


class TestCompiler(HashTreeTraverser):
    def __init__(self, group_level_elements: list):
        self.group_level_elements = group_level_elements
        self.sampler_package_saver: {Sampler, SamplePackage} = {}
        self.compiled_node = []

    def get_sample_package(self, sampler: Sampler) -> SamplePackage:
        return self.sampler_package_saver.get(sampler)

    def add_node(self, node, subtree) -> None:
        if isinstance(node, Sampler):
            self.__save_sampler_package(node, subtree)
        if isinstance(node, GenericController):
            self.__compile_controller(node, subtree)

    def subtract_node(self) -> None:
        pass

    def process_path(self) -> None:
        pass

    def __save_sampler_package(self, node, subtree):
        sample_package = SamplePackage()
        sample_package.add(subtree.list())  # 储存 Sampler下的子节点
        sample_package.add(self.group_level_elements)  # 把 group层的非 group节点添加至 Sampler节点下
        self.sampler_package_saver[node] = sample_package

    def __compile_controller(self, node, subtree):
        if node not in self.compiled_node:
            controller_level_elements = subtree.list()

            # Controller节点储存 Sampler节点和 Controller节点
            for element in controller_level_elements:
                if isinstance(element, Sampler) or isinstance(element, GenericController):
                    node.sub_samplers_and_controllers.append(element)

                if isinstance(element, LoopIterationListener):
                    node.add_iteration_listener(element)

            # 移除 Controller层的非 Sampler节点和非 Controller节点，用于传递到子代
            self.__remove_samplers_and_controllers(controller_level_elements)

            # 合并 Group层和子代 Controller层的非 Sampler节点和非 Controller节点
            parent_level_elements = self.group_level_elements + controller_level_elements

            # 递归编译子代节点
            test_compiler = TestCompiler(parent_level_elements)
            subtree.traverse(test_compiler)
            self.sampler_package_saver.update(test_compiler.sampler_package_saver)

            # 存储已编译过的 controller节点，避免递归遍历下有可能产生重复编译的问题
            self.compiled_node.extend(test_compiler.compiled_node)
            self.compiled_node.append(node)

    @staticmethod
    def __remove_samplers_and_controllers(elements: list):
        for element in elements[:]:
            if (
                    isinstance(element, Sampler) or
                    isinstance(element, GenericController) or
                    not isinstance(element, TestElement)
            ):
                elements.remove(element)


class FindTestElementsUpToRoot(HashTreeTraverser):
    def __init__(self, required_nodes: object):
        self.node_list = []
        self.required_nodes = required_nodes
        self.stop_recording = False

    def get_controllers_to_root(self) -> list:
        result = []
        node_list = self.node_list[::-1]
        for node in node_list:
            if isinstance(node, Controller):
                result.append(node)
        return result

    def add_node(self, node, subtree) -> None:
        if self.stop_recording:
            return

        if node is self.required_nodes:
            self.stop_recording = True

        self.node_list.append(node)

    def subtract_node(self) -> None:
        if self.stop_recording:
            return

        self.node_list.pop()  # 删除最后一个

    def process_path(self) -> None:
        pass
