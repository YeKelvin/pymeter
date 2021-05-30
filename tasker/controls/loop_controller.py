#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : loop_controller
# @Time    : 2020/2/28 17:16
# @Author  : Kelvin.Ye
from typing import Optional

from tasker.controls.controller import IteratingController
from tasker.controls.generic_controller import GenericController
from tasker.elements.element import TaskElement
from tasker.engine.interface import LoopIterationListener
from tasker.groups.context import ContextService
from tasker.groups.group import TaskGroup
from tasker.samplers.sampler import Sampler
from tasker.utils.log_util import get_logger


log = get_logger(__name__)


class LoopController(TaskElement, GenericController, IteratingController, LoopIterationListener):
    # 循环次数
    LOOPS = 'LoopController__loops'

    # 是否无限循环
    CONTINUE_FOREVER = 'LoopController__continue_forever'

    # 无限循环数
    INFINITE_LOOP_COUNT = -1

    def __init__(self):
        TaskElement.__init__(self)
        GenericController.__init__(self)

        self.loop_count: int = 0
        self.break_loop: bool = False

    @property
    def loops(self) -> int:
        return self.get_property_as_int(self.LOOPS)

    @property
    def continue_forever(self) -> bool:
        """循环控制器始终将continue_forever设置为true，以便下次父级调用它们时执行它们"""
        if isinstance(self, TaskGroup):
            return self.get_property_as_bool(self.CONTINUE_FOREVER)
        return True

    @property
    def done(self):
        return GenericController.done

    @done.setter
    def done(self, value: bool):
        log.debug(f'协程:[ {ContextService.get_context().coroutine_name} ] 控制器:[ {self.name} ] done:[ {value} ]')
        self.reset_break_loop()
        GenericController.done = value

    def next(self) -> Optional[Sampler]:
        if self.end_of_loop():
            if not self.continue_forever:
                self.done = True
            self.reset_break_loop()
            return None

        if self.first:
            if not self.continue_forever:
                log.info(
                    f'协程:[ {ContextService.get_context().coroutine_name} ] '
                    f'控制器:[ {self.name} ] 开始第 {self.loop_count + 1} 次迭代'
                )
            else:
                log.info(f'协程:[ {ContextService.get_context().coroutine_name} ] 控制器:[ {self.name} ] 开始新的迭代')

        return super().next()

    def trigger_end_of_loop(self):
        """触发循环结束
        """
        self.reset_loop_count()
        super().trigger_end_of_loop()

    def end_of_loop(self) -> bool:
        """判断循环是否结束
        """
        return self.break_loop or (self.loops > self.INFINITE_LOOP_COUNT) and (self.loop_count >= self.loops)

    def next_is_null(self):
        self.re_initialize()
        if self.end_of_loop():
            if not self.continue_forever:
                self.done = True
            else:
                self.reset_loop_count()
            return None
        return self.next()

    def increment_loop_count(self):
        self.loop_count += 1

    def reset_loop_count(self):
        self.loop_count = 0

    def re_initialize(self):
        self.first = True
        self.reset_current()
        self.increment_loop_count()

    def reset_break_loop(self):
        if self.break_loop:
            self.break_loop = False

    def start_next_loop(self):
        self.re_initialize()

    def break_loop(self):
        self.break_loop = True
        self.first = True
        self.reset_current()
        self.reset_loop_count()

    def iteration_start(self, source, iter_count):
        self.re_initialize()
        self.reset_loop_count()
