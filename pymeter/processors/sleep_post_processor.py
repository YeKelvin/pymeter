#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sleep_post_processor.py
# @Time    : 2022/10/17 17:05
# @Author  : Kelvin.Ye
import traceback
from typing import Final

import gevent

from pymeter.processors.pre import PreProcessor
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class SleepPostProcessor(PreProcessor):

    # 延迟时间，单位ms
    DELAY: Final = 'SleepPostProcessor__delay'

    @property
    def delay(self):
        return self.get_property_as_str(self.DELAY)

    def process(self) -> None:
        # noinspection PyBroadException
        try:
            log.debug(f'元素:[{self.name}] 后置等待 {self.delay} ms')
            gevent.sleep(float(self.delay) / 1000)
        except Exception:
            log.error(traceback.format_exc())
