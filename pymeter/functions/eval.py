#!/usr/bin python3
# @File    : eval.py
# @Time    : 2020/1/20 16:08
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger

from pymeter.engine import values
from pymeter.functions.function import Function


class Eval(Function):

    REF_KEY: Final = '__Eval'

    def __init__(self):
        self.parameter = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')
        parameter = self.parameter.execute().strip()
        # TODO: 待优化，解决循环引用
        return values.CompoundVariable(parameter).execute().strip()

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_count(params, 1)
        # 提取参数
        self.parameter = params[0]
