#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : time.py
# @Time    : 2020/1/20 16:07
# @Author  : Kelvin.Ye
import time
from typing import Final

from pymeter.functions.function import Function
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class Time(Function):

    REF_KEY: Final = '__Time'

    def __init__(self):
        self.format = None

    def execute(self):
        log.debug(f'start execute function:[ {self.REF_KEY} ]')

        timestamp = time.time()

        # 格式化时间
        if self.format:
            time_format = self.format.execute().strip()
            struct_time = time.localtime(timestamp)
            result = time.strftime(time_format, struct_time)
            return result

        result = str(int(timestamp * 1000))
        log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        log.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        self.check_parameter_min(params, 0)
        self.check_parameter_max(params, 1)

        if len(params) > 0:
            self.format = params[0]
