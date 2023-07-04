#!/usr/bin python3
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
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')

        if self.length:
            length = int(self.length.execute().strip())
            return ''.join([str(random.randint(0, 9)) for _ in range(length)])

        return str(random.random()).replace('0.', '')

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_min(params, 0)
        self.check_parameter_max(params, 1)
        # 提取参数
        self.length = params[0] if params else None
