#!/usr/bin python3
# @File    : minute.py
# @Time    : 2023-08-21 15:35:17
# @Author  : Kelvin.Ye
from typing import Final

import arrow
from loguru import logger

from pymeter.functions.function import Function


class Minute(Function):

    REF_KEY: Final = '__minute'

    def __init__(self):
        self.offset = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')

        now = arrow.now()

        if self.offset:
            now = now.shift(minutes=int(self.offset.execute().strip()))

        return str(now.minute)

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_min(params, 0)
        self.check_parameter_max(params, 1)
        # 提取参数
        self.offset = params[0] if params else None
