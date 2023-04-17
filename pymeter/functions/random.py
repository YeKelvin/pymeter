#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : random.py
# @Time    : 2020/1/20 16:06
# @Author  : Kelvin.Ye
import random
from typing import Final

from loguru import logger

from pymeter.functions.function import Function


class Random(Function):

    REF_KEY: Final = '__Random'

    def __init__(self):
        self.length = None

    def execute(self):
        logger.debug(f'start execute function:[ {self.REF_KEY} ]')

        if self.length:
            length = int(self.length.execute().strip())
            result = ''.join([str(random.randint(0, 9)) for _ in range(length)])
            logger.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')
            return result

        result = str(random.random()).replace('0.', '')
        logger.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')
        return result

    def set_parameters(self, params: list):
        logger.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        # 校验函数参数个数
        self.check_parameter_min(params, 0)
        self.check_parameter_max(params, 1)
        # 提取参数
        self.length = params[0] if params else None
