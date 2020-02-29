#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : loop_controller
# @Time    : 2020/2/28 17:16
# @Author  : Kelvin.Ye
from typing import Union

from sendanywhere.controls.generic_controller import GenericController
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class LoopController(GenericController, TestElement):
    # 是否无限循环
    CONTINUE_FOREVER = 'LoopController.continue_forever'

    # 循环次数
    LOOPS = 'LoopController.loops'

    # 无限循环数
    INFINITE_LOOP_COUNT = -1

    def __init__(self, name: str = None, comments: str = None, propertys: dict = None):
        GenericController.__init__(self)
        TestElement.__init__(self, name, comments, propertys)
        self.loop_count = 0
        self.break_loop = False

    @property
    def loops(self) -> int:
        return self.get_property_as_int(self.LOOPS)

    @property
    def continue_forever(self) -> bool:
        return self.get_property_as_bool(self.CONTINUE_FOREVER)

    def next(self) -> Union[Sampler, None]:
        if self.end_of_loop():
            if not self.continue_forever:
                self.set_done(True)
            self.reset_break_loop()
            return None
        return super().next()

    def initialize(self):
        pass

    def trigger_end_of_loop(self):
        super().trigger_end_of_loop()
        self.reset_loop_count()

    def end_of_loop(self):
        return self.break_loop or (self.loops > self.INFINITE_LOOP_COUNT) and (self.loop_count >= self.loops)

    def set_done(self, is_done: bool):
        self.reset_break_loop()
        super().set_done(is_done)

    def next_is_null(self):
        self.re_initialize()
        if self.end_of_loop():
            if not self.continue_forever:
                self.set_done(True)
            else:
                self.reset_loop_count()
            return None
        return self.next()

    def increment_loop_count(self):
        self.loop_count += 1

    def reset_loop_count(self):
        self.loop_count = 0

    def re_initialize(self):
        self.set_first(True)
        self.reset_current()
        self.increment_loop_count()

    def start_next_loop(self):
        self.re_initialize()

    def reset_break_loop(self):
        if self.break_loop:
            self.break_loop = False

    def break_loop(self):
        self.break_loop = True
        self.set_first(True)
        self.reset_current()
        self.reset_loop_count()

    def iteration_start(self):
        pass
