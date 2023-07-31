#!/usr/bin python3
# @File    : random.py
# @Time    : 2020/1/20 16:06
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger

from pymeter.functions.function import Function
from pymeter.utils.random_util import get_phone_number


class Phone(Function):

    REF_KEY: Final = '__phone'

    def __init__(self):
        # 通讯运营商，默认ALL，可选 CMCC | CUCC | TELECOM
        self.operator = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')
        operator = self.operator.execute().strip() if self.operator else 'ALL'
        return get_phone_number(operator)

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_min(params, 0)
        self.check_parameter_max(params, 1)
        # 提取参数
        self.operator = params[0] if params else None
