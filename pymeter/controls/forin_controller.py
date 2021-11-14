#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : forin_controller.py
# @Time    : 2021/11/12 14:42
# @Author  : Kelvin.Ye
import traceback
from collections import Iterable
from typing import Final

import gevent

from pymeter.controls.controller import IteratingController
from pymeter.controls.generic_controller import GenericController
from pymeter.utils.json_util import from_json
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class ForInController(GenericController, IteratingController):

    FOR_CODE: Final = 'ForInController__for_code'

    IN_CODE: Final = 'ForInController__in_code'

    USE_VARIABLES: Final = 'ForInController__use_variables'

    DELAY: Final = 'ForInController__delay'

    @property
    def for_code(self) -> str:
        return self.get_property_as_str(self.FOR_CODE)

    @property
    def in_code(self) -> str:
        return self.get_property_as_str(self.IN_CODE)

    @property
    def use_variables(self) -> bool:
        return self.get_property_as_bool(self.USE_VARIABLES)

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

        if isinstance(self._instance, dict):
            for i in range(self._keys_length):
                self.ctx.variables.put(self._keys[i], self._instance[self._loop_count][i])
        else:
            self.ctx.variables.put(self._keys[0], self._instance[self._loop_count])

        return self._done

    @done.setter
    def done(self, val: bool):
        self._done = val

    def __init__(self):
        super().__init__()
        self._loop_count: int = 0
        self._break_loop: bool = False
        self._instance = None
        self._keys = None
        self._keys_length = 0
        self._end_index = 0

    def initial_forin_instance(self):
        if self.use_variables:
            self._instance = self.ctx.variables.get(self.in_code)
        else:
            self._instance = from_json(self.in_code)

        if isinstance(self._instance, str):
            self._instance = from_json(self._instance)

        if not isinstance(self._instance, Iterable):
            log.error(f'in:[ {self.in_code} ] 不是可迭代的对象')
            self.done = True
            return

        if isinstance(self._instance, dict):
            self._instance = list(self._instance.items())

        self._keys = self.for_code.split(',')
        self._keys_length = len(self._keys)
        for i, key in enumerate(self._keys):
            self._keys[i] = key.strip()

        self._end_index = len(self._instance)

    def next(self):
        """@override"""
        self.update_iteration_index(self.name, self._loop_count)
        # noinspection PyBroadException
        try:
            if self.first:
                self.initial_forin_instance()

            if self.end_of_loop():
                self.reset_break_loop()
                return None

            if self.delay:
                log.debug(
                    f'coroutine:[ {self.ctx.coroutine_name} ] controller:[ {self.name} ] delay:[ {self.delay}ms ]')
                gevent.sleep(float(self.delay / 1000))

            return super().next()
        except Exception:
            log.debug(traceback.format_exc())
        finally:
            self.update_iteration_index(self.name, self._loop_count)

    def trigger_end_of_loop(self):
        """触发循环结束"""
        super().trigger_end_of_loop()
        self.reset_loop_count()

    def end_of_loop(self) -> bool:
        """判断循环是否结束"""
        return self._break_loop or (self._loop_count >= self._end_index)

    def next_is_null(self):
        self.re_initialize()
        if self.end_of_loop():
            self.reset_loop_count()
            return None
        return self.next()

    def increment_loop_count(self):
        self._loop_count += 1

    def reset_loop_count(self):
        self._loop_count = 0

    def re_initialize(self):
        self.first = True
        self.reset_current()
        self.increment_loop_count()
        self.recover_running_version()

    def reset_break_loop(self):
        if self._break_loop:
            self._break_loop = False

    def start_next_loop(self):
        self.re_initialize()

    def break_loop(self):
        self._break_loop = True
        self.first = True
        self.reset_current()
        self.reset_loop_count()
        self.recover_running_version()

    def iteration_start(self, source, iter_count):
        self.re_initialize()
        self.reset_loop_count()
