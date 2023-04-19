#!/usr/bin python3
# @File    : hex.py
# @Time    : 2022/10/13 17:19
# @Author  : Kelvin.Ye
import binascii
from typing import Final

from loguru import logger

from pymeter.functions.function import Function


class Hex(Function):

    REF_KEY: Final = '__Hex'

    def __init__(self):
        self.data = None

    def execute(self):
        logger.debug(f'start execute function:[ {self.REF_KEY} ]')

        data = self.data.execute().strip()

        result = binascii.b2a_hex(data).decode('utf8')
        logger.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        logger.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        # 校验函数参数个数
        self.check_parameter_count(params, 1)
        # 提取参数
        self.data = params[0]
