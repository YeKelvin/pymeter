#!/usr/bin python3
# @File    : foreach_controller.py
# @Time    : 2021/11/12 14:42
# @Author  : Kelvin.Ye
from collections.abc import Iterable
from typing import Final

import gevent
from loguru import logger

from pymeter.controls.controller import IteratingController
from pymeter.controls.generic_controller import GenericController
from pymeter.utils.json_util import from_json


class ForeachController(GenericController, IteratingController):

    FOR_VARIABLE: Final = 'ForeachController__for_variable'

    IN_STATEMENT: Final = 'ForeachController__in_statement'

    DELAY: Final = 'ForeachController__delay'

    @property
    def for_variable(self) -> str:
        return self.get_property_as_str(self.FOR_VARIABLE)

    @property
    def in_statement(self) -> str:
        return self.get_property_as_str(self.IN_STATEMENT)

    @property
    def delay(self) -> int:
        return self.get_property_as_int(self.DELAY)

    @property
    def iter_count(self) -> int:
        return self._loop_count + 1

    @property
    def done(self) -> bool:
        if self._loop_count >= self._end_index:
            return True

        if isinstance(self._iterable_object, dict) and self._forvar_length == 2:
            for i in range(self._forvar_length):
                self.ctx.variables.put(self._forvar_list[i], self._iterable_object[self._loop_count][i])
        else:
            self.ctx.variables.put(self._forvar_list[0], self._iterable_object[self._loop_count])

        return self._done

    @done.setter
    def done(self, val: bool):
        self._done = val

    def __init__(self):
        super().__init__()
        self._loop_count: int = 0
        self._break_loop: bool = False
        self._forvar_list = None
        self._forvar_length = 0
        self._iterable_object = None
        self._end_index = 0

    def initial_forin(self):
        # 分割迭代变量
        self._forvar_list = self.for_variable.split(',')
        self._forvar_length = len(self._forvar_list)
        # 判断迭代变量的个数
        if self._forvar_length > 2:
            logger.error(f'for变量:[ {self.for_variable} ] 个数不合法，终止遍历')
            self.done = True
            return
        # 移除迭代变量首尾的空格
        for i, key in enumerate(self._forvar_list):
            self._forvar_list[i] = key.strip()

        # 获取迭代对象或反序列化对象
        self._iterable_object = self.ctx.variables.get(self.in_statement) or self.ctx.properties.get(self.in_statement)
        if isinstance(self._iterable_object, str):
            self._iterable_object = from_json(self._iterable_object)
        if self._iterable_object is None:
            self._iterable_object = from_json(self.in_statement)

        # 判断 in 对象是否为可迭代的对象
        if not isinstance(self._iterable_object, Iterable):
            logger.error(f'in对象:[ {self.in_statement} ] 不是可迭代的对象，终止遍历')
            self.done = True
            return

        # 判断迭代变量的个数决定使用 dict.values() 还是 items()
        if isinstance(self._iterable_object, dict):
            if self._forvar_length == 1:
                self._iterable_object = list(self._iterable_object.values())
            else:
                self._iterable_object = list(self._iterable_object.items())

        # 计算最后一个索引
        self._end_index = len(self._iterable_object)

    def next(self):
        """@override"""
        self.update_iteration_index(self.name, self._loop_count)
        # noinspection PyBroadException
        try:
            if self.first:
                self.initial_forin()

            if self.end_of_loop():
                logger.debug(f'线程:[ {self.ctx.thread_name} ] 控制器:[ {self.name} ] 获取下一个取样器')
                self.reset_break_loop()
                self.re_initialize()
                logger.debug(f'线程:[ {self.ctx.thread_name} ] 控制器:[ {self.name} ] 下一个为空')
                return None

            nsampler = super().next()
            if nsampler and self.delay:
                logger.debug(
                    f'线程:[ {self.ctx.thread_name} ] 控制器:[ {self.name} ] 间隔:[ {self.delay}ms ]'
                )
                gevent.sleep(float(self.delay / 1000))

            return nsampler
        except Exception:
            logger.exception('Exception Occurred')
        finally:
            self.update_iteration_index(self.name, self._loop_count)

    def trigger_end_of_loop(self):
        """@override"""
        super().trigger_end_of_loop()
        self.reset_loop_count()

    def end_of_loop(self) -> bool:
        """判断循环是否结束"""
        return self._break_loop or (self._loop_count >= self._end_index)

    def next_is_null(self):
        """@override"""
        self.re_initialize()
        if self.end_of_loop():
            self.reset_break_loop()
            self.reset_loop_count()
            return None
        return self.next()

    def increment_loop_count(self):
        self._loop_count += 1

    def reset_loop_count(self):
        self._loop_count = 0

    def re_initialize(self):
        """@override"""
        self.first = True
        self.reset_current()
        self.increment_loop_count()
        self.recover_running_version()

    def reset_break_loop(self):
        if self._break_loop:
            self._break_loop = False

    def start_next_loop(self):
        """@override"""
        logger.debug(f'线程:[ {self.ctx.thread_name} ] 控制器:[ {self.name} ] 开始下一个循环')
        self.re_initialize()

    def break_loop(self):
        """@override"""
        logger.debug(f'线程:[ {self.ctx.thread_name} ] 控制器:[ {self.name} ] 中止循环')
        self._break_loop = True
        self.first = True
        self.reset_current()
        self.reset_loop_count()
        self.recover_running_version()

    def iteration_start(self, source, iter_count):
        """@override"""
        self.re_initialize()
        self.reset_loop_count()
