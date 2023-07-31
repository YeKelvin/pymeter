#!/usr/bin python3
# @File    : random_int.py
# @Time    : 2021-08-17 23:46:00
# @Author  : Kelvin.Ye
import random
from typing import Final

from loguru import logger

from pymeter.functions.function import Function


class RandomInt(Function):

    REF_KEY: Final = '__random_int'

    def __init__(self):
        self.minimum = None
        self.maximum = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')

        minimum = int(self.minimum.execute().strip())
        maximum = int(self.maximum.execute().strip())

        return str(random.randint(minimum, maximum))

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_count(params, 2)
        # 提取参数
        self.minimum = params[0]
        self.maximum = params[1]
