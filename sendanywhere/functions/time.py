#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : time
# @Time    : 2020/1/20 16:07
# @Author  : Kelvin.Ye
import time
from sendanywhere.functions.function import Function
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class Time(Function):
    REF_KEY = '__Time'

    def __init__(self):
        self.var_name = None
        self.format = None

    def execute(self):
        log.debug(f'{self.REF_KEY} start execute')
        timestamp = int(time.time() * 1000)
        result = str(timestamp)

        if self.format:
            str_format = self.format.execute().strip()
            result = time.strftime(str_format, time.localtime(timestamp))

        if self.var_name:
            # todo 存在 var_name时放入变量中
            var_name = self.var_name.execute().strip()

        return result

    def set_parameters(self, parameters: list):
        log.debug(f'{self.REF_KEY} start to set parameters')
        if len(parameters) > 0:
            self.format = parameters[0]
        if len(parameters) > 1:
            self.var_name = parameters[1]
