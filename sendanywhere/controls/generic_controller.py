#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : generic_controller
# @Time    : 2020/2/28 17:25
# @Author  : Kelvin.Ye
from sendanywhere.controls.controller import Controller
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class GenericController(Controller):
    def __init__(self):
        # 存储 sampler或 controller
        self.samplers_and_controllers = []
        # sampler或 controller的索引
        self.current = 0
        # 当前迭代
        self.iter_count = 0
        # controller结束标识
        self.done = False
        # 第一个 sampler或 controller
        self.first = True

    def reset_current(self):
        self.current = 0

    def reset_iter_count(self):
        self.iter_count = 0

    def set_done(self, is_done: bool):
        self.done = is_done

    def set_first(self, is_first: bool):
        self.first = is_first

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

    def increment_iter_count(self):
        self.iter_count += 1

    def next(self) -> Sampler:
        if self.done:
            return None
        current_element = self.get_current_element()
        if current_element is None:
            return self.next_is_null()
        else:
            if isinstance(current_element, Sampler):
                return self.next_is_sampler()
            elif isinstance(current_element, Controller):
                return self.next_is_controller()

    def get_current_element(self):
        pass

    def next_is_sampler(self):
        pass

    def next_is_controller(self):
        pass

    def next_is_null(self):
        pass

    def add_element(self, element: Sampler or Controller):
        self.samplers_and_controllers.append(element)
