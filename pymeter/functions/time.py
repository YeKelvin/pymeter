#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : time
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
        self.var_name = None
        self.format = None

    def execute(self):
        log.debug(f'start execute function:[ {self.REF_KEY} ]')
        timestamp = time.time()
        result = str(int(timestamp * 1000))

        if self.format:
            # 格式化时间
            time_format = self.format.execute().strip()
            struct_time = time.localtime(timestamp)
            result = time.strftime(time_format, struct_time)

        if self.var_name:
            # 存在 var_name 时放入本地变量中
            var_name = self.var_name.execute().strip()
            self.variables.put(var_name, result)

        return result

    def set_parameters(self, parameters: list):
        log.debug(f'{self.REF_KEY} start to set parameters')
        if len(parameters) > 0:
            self.format = parameters[0]
        if len(parameters) > 1:
            self.var_name = parameters[1]
