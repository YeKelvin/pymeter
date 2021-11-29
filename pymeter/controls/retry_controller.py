#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : retry_controller.py
# @Time    : 2021/11/29 11:25
# @Author  : Kelvin.Ye
import traceback
from typing import Final
from typing import Optional

import gevent

from pymeter.controls.controller import IteratingController
from pymeter.controls.generic_controller import GenericController
from pymeter.elements.element import TestElement
from pymeter.engine.interface import LoopIterationListener
from pymeter.samplers.sampler import Sampler
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class RetryController(GenericController, IteratingController, LoopIterationListener):

    # 重试次数
    RETRIES: Final = 'RetryController__retries'

    # 重试间隔
    INTERVALS: Final = 'RetryController__intervals'

    def __init__(self):
        TestElement.__init__(self)
        GenericController.__init__(self)

        self._retry_count: int = 0
        self._break_retry: bool = False

    @property
    def retries(self) -> int:
        return self.get_property_as_int(self.RETRIES)

    @property
    def intervals(self) -> int:
        return self.get_property_as_int(self.INTERVALS)

    @property
    def done(self):
        """@override"""
        return self._done

    @done.setter
    def done(self, value: bool):
        """@override"""
        log.debug(f'coroutine:[ {self.ctx.coroutine_name} ] controller:[ {self.name} ] isDone:[ {value} ]')
        self.reset_break_retry()
        self._done = value

    def next(self) -> Optional[Sampler]:
        # noinspection PyBroadException
        try:
            if self.end_of_retry():
                self.reset_break_retry()
                return None

            # 给下一个 Sampler 添加重试标识
            nsampler = super().next()
            if self._retry_count < self.retries:
                nsampler.retrying = True
                nsampler.retry_count = self._retry_count

            # 重试延迟
            if not self.first and self.intervals:
                log.debug(
                    f'coroutine:[ {self.ctx.coroutine_name} ] controller:[ {self.name} ] '
                    f'retrying delay:[ {self.intervals}ms ]'
                )
                gevent.sleep(float(self.intervals / 1000))

            return nsampler
        except Exception:
            log.error(traceback.format_exc())

    def next_is_null(self):
        """@override"""
        self.re_initialize()
        if self.end_of_retry():
            self.reset_retry_count()
            return None
        return self.next()

    def end_of_retry(self) -> bool:
        return self._break_retry or (self._retry_count >= self.retries)

    def increment_retry_count(self):
        self._retry_count += 1

    def reset_retry_count(self):
        self._retry_count = 0

    def reset_break_retry(self):
        if self._break_retry:
            self._break_retry = False

    def trigger_end_of_loop(self):
        """@override"""
        super().trigger_end_of_loop()
        self.reset_retry_count()

    def re_initialize(self):
        """@override"""
        self.first = True
        self.reset_current()
        self.increment_retry_count()
        self.recover_running_version()

    def start_next_loop(self):
        """@override"""
        self.re_initialize()

    def break_loop(self):
        """@override"""
        self._break_retry = True
        self.first = True
        self.reset_current()
        self.reset_retry_count()
        self.recover_running_version()

    def iteration_start(self, source, iter_count):
        """@override"""
        self.re_initialize()
        self.reset_retry_count()
