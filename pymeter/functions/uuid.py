#!/usr/bin python3
# @Module  : functions
# @File    : uuid.py
# @Time    : 2024-03-11 18:06:27
# @Author  : Kelvin.Ye
import uuid
from typing import Final

from loguru import logger

from pymeter.functions.function import Function


class UUID(Function):

    REF_KEY: Final = '__uuid'

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')
        return str(uuid.uuid4())

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_count(params, 0)
