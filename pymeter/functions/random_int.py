#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : random_int.py
# @Time    : 2021-08-17 23:46:00
# @Author  : Kelvin.Ye
import random
from typing import Final

from pymeter.functions.function import Function
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class RandomInt(Function):

    REF_KEY: Final = '__RandomInt'

    def __init__(self):
        self.minimum = None
        self.maximum = None

    def execute(self):
        log.debug(f'start execute function:[ {self.REF_KEY} ]')

        minimum = int(self.minimum.execute().strip())
        maximum = int(self.maximum.execute().strip())

        result = str(random.randint(minimum, maximum))
        log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        log.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        # 校验函数参数个数
        self.check_parameter_count(params, 2)
        # 提取参数
        self.minimum = params[0]
        self.maximum = params[1]
