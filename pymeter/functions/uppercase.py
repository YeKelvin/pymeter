#!/usr/bin python3
# @Module  : functions
# @File    : uppercase.py
# @Time    : 2024-03-12 11:20:08
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger

from pymeter.functions.function import Function


class UpperCase(Function):

    REF_KEY: Final = '__uppercase'

    def __init__(self):
        self.data = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')

        data = self.data.execute().strip()
        return data.upper()

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_count(params, 1)
        # 提取参数
        self.data = params[0]
