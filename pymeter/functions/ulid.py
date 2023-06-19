#!/usr/bin python3
# @File    : random.py
# @Time    : 2020/1/20 16:06
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger
from ulid import microsecond as ulid

from pymeter.functions.function import Function


class ULID(Function):

    REF_KEY: Final = '__ULID'

    def execute(self):
        logger.debug(f'开始执行函数:[ {self.REF_KEY} ]')

        result = ulid.new().str
        logger.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')
        return result

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_count(params, 0)
