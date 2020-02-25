#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : traverser
# @Time    : 2020/2/25 15:06
# @Author  : Kelvin.Ye
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
    def add_node(self, key, subtree) -> None:
        pass

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
