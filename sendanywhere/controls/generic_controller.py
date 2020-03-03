#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : generic_controller
# @Time    : 2020/2/28 17:25
# @Author  : Kelvin.Ye
from typing import Union

from sendanywhere.controls.controller import Controller
from sendanywhere.engine.exceptions import NextIsNullException
from sendanywhere.engine.listener import LoopIterationListener
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class GenericController(Controller, LoopIterationListener):
    """所有控制器的基类
    """

    def __init__(self):
        super().__init__()

        # 存储 sampler或 controller
        self.samplers_and_controllers = []

        # sampler或 controller的索引
        self.current = 0

        # 当前迭代数
        self.iter_count = 0

        # 第一个 sampler或 controller
        self.is_first = True

    def reset_current(self):
        self.current = 0

    def reset_iter_count(self):
        self.iter_count = 0

    def set_done(self, is_done: bool):
        self.is_done = is_done

    def set_first(self, is_first: bool):
        self.is_first = is_first

    def initialize(self):
        """初始化 controller
        """
        self.reset_current()
        self.reset_iter_count()
        self.set_done(False)
        self.set_first(True)
        self.initialize_sub_controllers()

    def initialize_sub_controllers(self):
        """初始化子 controller
        """
        for element in self.samplers_and_controllers:
            if isinstance(element, Controller):
                element.initialize()

    def re_initialize(self):
        """重置 controller（在 controller的最后一个子代之后调用）
        """
        self.reset_current()
        self.increment_iter_count()
        self.set_first(True)

    def increment_current(self):
        self.current += 1

    def increment_iter_count(self):
        self.iter_count += 1

    def next(self) -> Union[Sampler, None]:
        if self.is_first:
            self.iteration_start()
            self.set_first(False)

        if self.is_done:
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
            pass

        return next_sampler

    def get_current_element(self):
        if self.current < len(self.samplers_and_controllers):
            return self.samplers_and_controllers[self.current]

        if not self.samplers_and_controllers:
            self.set_done(True)
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
        if controller.is_done:
            self.remove_current_element()
        else:
            self.increment_current()

    def add_element(self, element: Sampler or Controller):
        self.samplers_and_controllers.append(element)

    def remove_current_element(self):
        self.samplers_and_controllers.remove(self.samplers_and_controllers[self.current])

    def trigger_end_of_loop(self):
        self.re_initialize()

    def iteration_start(self):
        raise NotImplementedError
