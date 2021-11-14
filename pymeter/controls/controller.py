#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : controller.py
# @Time    : 2020/2/28 16:01
# @Author  : Kelvin.Ye
from abc import ABCMeta
from abc import abstractmethod

from pymeter.elements.element import TestElement
from pymeter.engine.interface import LoopIterationListener
from pymeter.groups.context import ContextService
from pymeter.samplers.sampler import Sampler


class Controller(TestElement, metaclass=ABCMeta):

    @abstractmethod
    @property
    def done(self):
        """是否已完成"""
        raise NotImplementedError

    @abstractmethod
    def next(self) -> Sampler:
        """返回下一个 Sampler，没有下一个时返回 None"""
        raise NotImplementedError

    @abstractmethod
    def initialize(self):
        """在迭代开始时调用以初始化控制器"""
        raise NotImplementedError

    @abstractmethod
    def trigger_end_of_loop(self):
        """在控制器上触发循环结束条件"""
        raise NotImplementedError

    @abstractmethod
    def add_iteration_listener(self, listener):
        raise NotImplementedError

    @abstractmethod
    def remove_iteration_listener(self, listener):
        raise NotImplementedError


class IteratingController(LoopIterationListener, metaclass=ABCMeta):
    """迭代控制器"""

    @abstractmethod
    def start_next_loop(self) -> None:
        """开始下一个迭代"""
        raise NotImplementedError

    @abstractmethod
    def break_loop(self) -> None:
        """中断循环"""
        raise NotImplementedError

    def update_iteration_index(self, name, iter_count) -> None:
        variables = ContextService.get_context().variables
        if variables:
            variables.put(f'__pm__.{name}.__idx__', iter_count)
