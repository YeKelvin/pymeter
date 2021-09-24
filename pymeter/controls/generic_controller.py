#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : generic_controller
# @Time    : 2020/2/28 17:25
# @Author  : Kelvin.Ye
from typing import Optional

from pymeter.common.exceptions import NextIsNullException
from pymeter.controls.controller import Controller
from pymeter.engine.interface import LoopIterationListener
from pymeter.engine.interface import TestCompilerHelper
from pymeter.groups.context import ContextService
from pymeter.groups.context import CoroutineContext
from pymeter.samplers.sampler import Sampler
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class GenericController(Controller, TestCompilerHelper):
    """所有控制器的基类"""

    def __init__(self):
        super().__init__()
        self.children = []

        # 存储Sampler或Controller
        self.sub_controllers_and_samplers = []

        # 存储子代控制器的LoopIterationListener
        self.sub_iteration_listeners = []

        # Sampler或Controller的索引
        self.current = 0

        # 当前迭代数
        self.iter_count = 0

        # 第一个Sampler或Controller
        self.first = True

        # 当控制器完成所有Sampler的交付时，设置为True，表示协程已完成
        self._done = False  # @override

    @property
    def done(self) -> bool:
        return self._done

    @done.setter
    def done(self, val: bool):
        self._done = val

    @property
    def ctx(self) -> CoroutineContext:
        return ContextService.get_context()

    def reset_current(self):
        self.current = 0

    def reset_iter_count(self):
        self.iter_count = 0

    def initialize(self):
        """初始化Controller"""
        self.done = False
        self.first = True
        self.reset_current()
        self.reset_iter_count()
        self.initialize_sub_controllers()

    def initialize_sub_controllers(self):
        """初始化子Controller"""
        for element in self.sub_controllers_and_samplers:
            if isinstance(element, GenericController):
                element.initialize()

    def re_initialize(self):
        """重置Controller（在Controller的最后一个子代之后调用）"""
        self.reset_current()
        self.increment_iter_count()
        self.first = True
        self.recover_running_version()

    def increment_current(self):
        self.current += 1

    def increment_iter_count(self):
        self.iter_count += 1

    def next(self) -> Optional[Sampler]:
        log.debug(f'coroutine:[ {self.ctx.coroutine_name} ] controller:[ {self.name} ] start to get next')
        self.fire_iter_events()

        if self.done:
            return None

        next = None
        try:
            current_element = self.get_current_element()
            if current_element is None:
                next = self.next_is_null()
            else:
                if isinstance(current_element, Sampler):
                    next = self.next_is_sampler(current_element)
                else:
                    next = self.next_is_controller(current_element)
        except NextIsNullException:
            log.debug(f'coroutine:[ {self.ctx.coroutine_name} ] controller:[ {self.name} ] next is null')

        log.debug(f'coroutine:[ {self.ctx.coroutine_name} ] controller:[ {self.name} ] next:[ {next} ]')
        return next

    def fire_iter_events(self):
        if self.first:
            self.fire_iteration_start()
            self.first = False

    def fire_iteration_start(self):
        log.debug(f'coroutine:[ {self.ctx.coroutine_name} ] notify all LoopIterationListener to start')
        for listener in self.sub_iteration_listeners[::-1]:
            listener.iteration_start(self, self.iter_count)

    def get_current_element(self):
        if self.current < len(self.sub_controllers_and_samplers):
            return self.sub_controllers_and_samplers[self.current]

        if not self.sub_controllers_and_samplers:
            self.done = True
            raise NextIsNullException()

        return None

    def next_is_sampler(self, sampler: Sampler) -> Sampler:
        self.increment_current()
        return sampler

    def next_is_controller(self, controller: Controller) -> Sampler:
        sampler = controller.next()
        if sampler is None:
            self.current_returned_none(controller)
            sampler = self.next()
        return sampler

    def next_is_null(self) -> None:
        self.re_initialize()
        return None

    def current_returned_none(self, controller: Controller):
        if controller.done:
            self.remove_current_element()
        else:
            self.increment_current()

    def add_element(self, child):
        log.debug(f'coroutine:[ {self.ctx.coroutine_name} ] controller:[ {self.name} ] add element:[ {child} ]')
        self.sub_controllers_and_samplers.append(child)

    def add_test_element(self, child):
        if isinstance(child, Controller) or isinstance(child, Sampler):
            self.add_element(child)

    def add_test_element_once(self, child) -> bool:
        """@override from TestCompilerHelper"""
        if child not in self.children:
            self.children.append(child)
            self.add_test_element(child)
            return True
        else:
            return False

    def remove_current_element(self):
        self.sub_controllers_and_samplers.remove(self.sub_controllers_and_samplers[self.current])

    def add_iteration_listener(self, listener: LoopIterationListener):
        log.debug(
            f'coroutine:[ {self.ctx.coroutine_name} ] controller:[ {self.name} ] add iteration listener:[ {listener} ] '
        )
        self.sub_iteration_listeners.append(listener)

    def remove_iteration_listener(self, listener: LoopIterationListener):
        self.sub_iteration_listeners.remove(listener)

    def trigger_end_of_loop(self):
        self.re_initialize()
