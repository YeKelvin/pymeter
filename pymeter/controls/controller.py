#!/usr/bin python3
# @File    : controller.py
# @Time    : 2020/2/28 16:01
# @Author  : Kelvin.Ye
from abc import ABCMeta
from abc import abstractmethod

from pymeter.elements.element import TestElement
from pymeter.engines.interface import LoopIterationListener
from pymeter.samplers.sampler import Sampler
from pymeter.workers.context import ContextService


class Controller(TestElement):

    @property
    def done(self):
        """是否已完成"""
        raise NotImplementedError

    def next(self) -> Sampler:
        """返回下一个 Sampler，没有下一个时返回 None"""
        raise NotImplementedError

    def initialize(self):
        """在迭代开始时调用以初始化控制器"""
        raise NotImplementedError

    def trigger_end_of_loop(self):
        """在控制器上触发循环结束条件"""
        raise NotImplementedError

    def add_iteration_listener(self, listener):
        raise NotImplementedError

    def remove_iteration_listener(self, listener):
        raise NotImplementedError


class IteratingController(LoopIterationListener, metaclass=ABCMeta):
    """迭代控制器"""

    PREFIX = '__pm__'
    SUFFIX = '__idx__'

    @abstractmethod
    def start_next_loop(self) -> None:
        """开始下一个迭代"""
        raise NotImplementedError

    @abstractmethod
    def break_loop(self) -> None:
        """中断循环"""
        raise NotImplementedError

    def update_iteration_index(self, name, iter_count) -> None:
        if variables := ContextService.get_context().variables:
            variables.put(f'{self.PREFIX}.{name}.{self.SUFFIX}', iter_count)
