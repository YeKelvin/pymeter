#!/usr/bin python3
# @File    : day.py
# @Time    : 2023-08-21 14:46:35
# @Author  : Kelvin.Ye
from typing import Final

import arrow
from loguru import logger

from pymeter.functions.function import Function


class Day(Function):

    REF_KEY: Final = '__day'

    def __init__(self):
        self.offset = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')

        now = arrow.now()

        if self.offset:
            now = now.shift(days=int(self.offset.execute().strip()))

        return str(now.day)

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_min(params, 0)
        self.check_parameter_max(params, 1)
        # 提取参数
        self.offset = params[0] if params else None
