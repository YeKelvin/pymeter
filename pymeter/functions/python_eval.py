#!/usr/bin python3
# @File    : python_eval.py
# @Time    : 2023-08-29 16:35:52
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger

from pymeter.functions.function import Function


class PythonEval(Function):

    REF_KEY: Final = '__python_eval'

    def __init__(self):
        self.expression = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')
        return eval(self.expression.execute().strip())

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_min(params, 1)
        self.check_parameter_max(params, 1)
        # 提取参数
        self.expression = params[0]
