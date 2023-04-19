#!/usr/bin python3
# @File    : constant_timer.py
# @Time    : 2021/10/14 19:02
# @Author  : Kelvin.Ye
from timers.timer import Timer


class ConstantTimer(Timer):

    # 延迟时间，单位ms
    DELAY = 'ConstantTimer__delay'

    def delay(self):
        return self.get_property_as_float(self.DELAY)
