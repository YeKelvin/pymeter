#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : loop_controller
# @Time    : 2020/2/28 17:16
# @Author  : Kelvin.Ye
from typing import Union

from sendanywhere.controls.controller import IteratingController
from sendanywhere.controls.generic_controller import GenericController
from sendanywhere.coroutines.context import ContextService
from sendanywhere.engine.interface import LoopIterationListener
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class LoopController(GenericController, IteratingController, LoopIterationListener, TestElement):
    # 循环次数
    LOOPS = 'LoopController__loops'

    # 是否无限循环
    CONTINUE_FOREVER = 'LoopController__continue__forever'

    # 无限循环数
    INFINITE_LOOP_COUNT = -1

    def __init__(self, name: str = None, comments: str = None):
        GenericController.__init__(self)
        TestElement.__init__(self, name, comments)
        self.loop_count = 0
        self.is_break_loop = False

    @property
    def loops(self) -> int:
        return self.get_property_as_int(self.LOOPS)

    @property
    def continue_forever(self) -> bool:
        """循环控制器始终将 continue_forever设置为 true，以便下次父级调用它们时执行它们
        """
        from sendanywhere.coroutines.group import CoroutineGroup
        if isinstance(self, CoroutineGroup):
            return self.get_property_as_bool(self.CONTINUE_FOREVER)
        return True

    def next(self) -> Union[Sampler, None]:
        if self.end_of_loop():
            if not self.continue_forever:
                self.set_done(True)
            self.reset_break_loop()
            return None

        if self.is_first:
            if not self.continue_forever:
                log.info(
                    f'协程:[{ContextService.get_context().coroutine_name}] '
                    f'控制器:[{self.name}] 开始第 {self.loop_count + 1} 次迭代'
                )
            else:
                log.info(f'协程:[{ContextService.get_context().coroutine_name}] 控制器:[{self.name}] 开始新的迭代')

        return super().next()

    def trigger_end_of_loop(self):
        """触发循环结束
        """
        self.reset_loop_count()
        super().trigger_end_of_loop()

    def end_of_loop(self) -> bool:
        """判断循环是否结束
        """
        return self.is_break_loop or (self.loops > self.INFINITE_LOOP_COUNT) and (self.loop_count >= self.loops)

    def set_done(self, is_done: bool):
        log.debug(
            f'coroutine:[{ContextService.get_context().coroutine_name}] '
            f'controller:[{self.name}] set done = {is_done}'
        )
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

    def reset_break_loop(self):
        if self.is_break_loop:
            self.is_break_loop = False

    def start_next_loop(self):
        self.re_initialize()

    def break_loop(self):
        self.is_break_loop = True
        self.set_first(True)
        self.reset_current()
        self.reset_loop_count()

    def iteration_start(self, source, iter_count):
        self.re_initialize()
        self.reset_loop_count()
