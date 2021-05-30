#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : generic_controller
# @Time    : 2020/2/28 17:25
# @Author  : Kelvin.Ye
import traceback
from typing import Optional

from tasker.common.exceptions import NextIsNullException
from tasker.controls.controller import Controller
from tasker.engine.interface import LoopIterationListener
from tasker.groups.context import ContextService
from tasker.samplers.sampler import Sampler
from tasker.utils.log_util import get_logger


log = get_logger(__name__)


class GenericController(Controller):
    """所有控制器的基类
    """

    def __init__(self):
        super().__init__()

        # 存储Sampler或Controller
        self.sub_samplers_and_controllers = []

        # 存储子代控制器的LoopIterationListener
        self.sub_iteration_listeners = []

        # Sampler或Controller的索引
        self.current = 0

        # 当前迭代数
        self.iter_count = 0

        # 第一个Sampler或Controller
        self.first = True

        # 当控制器完成所有Sampler的交付时，设置为True，表示协程已完成
        self._done = False

    @property
    def done(self):
        return self._done

    @done.setter
    def done(self, value: bool):
        self._done = value

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
        for element in self.sub_samplers_and_controllers:
            if isinstance(element, GenericController):
                element.initialize()

    def re_initialize(self):
        """重置Controller（在Controller的最后一个子代之后调用）"""
        self.reset_current()
        self.increment_iter_count()
        self.first = True

    def increment_current(self):
        self.current += 1

    def increment_iter_count(self):
        self.iter_count += 1

    def next(self) -> Optional[Sampler]:
        log.debug('获取下一个Sampler')
        self.fire_iter_events()

        if self.done:
            return None

        next_sampler = None
        try:
            current_element = self.get_current_element()
            if current_element is None:
                next_sampler = self.next_is_null()
            else:
                if isinstance(current_element, Sampler):
                    next_sampler = self.next_is_sampler(current_element)
                elif isinstance(current_element, Controller):
                    next_sampler = self.next_is_controller(current_element)
        except NextIsNullException:
            log.debug(traceback.format_exc())

        log.debug(f'下一个Sampler:[ {next_sampler} ]')
        return next_sampler

    def fire_iter_events(self):
        if self.first:
            self.fire_iteration_start()
            self.first = False

    def fire_iteration_start(self):
        log.debug(
            f'notify all LoopIterationListener to start, coroutine:[ {ContextService.get_context().coroutine_name} ]'
        )
        for listener in self.sub_iteration_listeners[::-1]:
            listener.iteration_start(self, self.iter_count)

    def get_current_element(self):
        if self.current < len(self.sub_samplers_and_controllers):
            return self.sub_samplers_and_controllers[self.current]

        if not self.sub_samplers_and_controllers:
            self.done = True
            raise NextIsNullException()

        return None

    def next_is_sampler(self, sampler: Sampler):
        self.increment_current()
        return sampler

    def next_is_controller(self, controller: Controller):
        sampler = controller.next()
        if sampler is None:
            self.current_returned_none(controller)
            sampler = self.next()
        return sampler

    def next_is_null(self):
        self.re_initialize()
        return None

    def current_returned_none(self, controller: Controller) -> None:
        if controller.done:
            self.remove_current_element()
        else:
            self.increment_current()

    def add_element(self, element: Sampler or Controller):
        self.sub_samplers_and_controllers.append(element)

    def remove_current_element(self):
        self.sub_samplers_and_controllers.remove(self.sub_samplers_and_controllers[self.current])

    def add_iteration_listener(self, listener: LoopIterationListener):
        self.sub_iteration_listeners.append(listener)

    def remove_iteration_listener(self, listener: LoopIterationListener):
        self.sub_iteration_listeners.remove(listener)

    def trigger_end_of_loop(self):
        self.re_initialize()
