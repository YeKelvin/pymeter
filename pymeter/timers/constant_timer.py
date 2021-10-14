#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : constant_timer.py
# @Time    : 2021/10/14 19:02
# @Author  : Kelvin.Ye
from timers.timer import Timer

from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class ConstantTimer(Timer):

    # 延迟事件
    DELAY = 'ConstantTimer__delay'

    def delay(self):
        return self.get_property_as_float(self.DELAY)
