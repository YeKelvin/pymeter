#!/usr/bin python3
# @File    : fake_name.py
# @Time    : 2023-06-19 14:58:52
# @Author  : Kelvin.Ye
from typing import Final

from faker import Faker
from loguru import logger

from pymeter.functions.function import Function


class FakeName(Function):
    """伪造一个名称"""

    REF_KEY: Final = '__FakeName'

    def __init__(self):
        self.locale = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')
        locale = self.locale.execute().strip() if self.locale else 'zh_CN'
        return Faker(locale=locale).name()

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_max(params, 1)
        # 提取参数
        if params:
            self.locale = params[0]
