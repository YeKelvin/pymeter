#!/usr/bin python3
# @File    : hex.py
# @Time    : 2022/10/13 17:19
# @Author  : Kelvin.Ye
import binascii
from typing import Final

from loguru import logger

from pymeter.functions.function import Function


class Hex(Function):

    REF_KEY: Final = '__hex'

    def __init__(self):
        self.data = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')
        data = self.data.execute().strip()
        return binascii.b2a_hex(data).decode('utf8')

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_count(params, 1)
        # 提取参数
        self.data = params[0]
