#!/usr/bin python3
# @File    : fake_phone_number.py
# @Time    : 2023-06-19 15:00:06
# @Author  : Kelvin.Ye
from typing import Final

from faker import Faker
from loguru import logger

from pymeter.functions.function import Function


class FakePhoneNumber(Function):
    """伪造一个手机号"""

    REF_KEY: Final = '__FakePhoneNumber'

    def __init__(self):
        self.locale = None

    def execute(self):
        logger.debug(f'开始执行函数:[ {self.REF_KEY} ]')
        locale = self.locale.execute().strip() if self.locale else 'zh_CN'
        return Faker(locale=locale).phone_number()

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_max(params, 1)
        # 提取参数
        if params:
            self.locale = params[0]
