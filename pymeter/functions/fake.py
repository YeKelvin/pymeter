#!/usr/bin python3
# @File    : fake.py
# @Time    : 2023-06-19 12:12:07
# @Author  : Kelvin.Ye
from typing import Final

from faker import Faker
from loguru import logger

from pymeter.functions.function import Function


class Fake(Function):

    REF_KEY: Final = '__fake'

    def __init__(self):
        self.provider = None
        self.locale = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')
        generator = self.provider.execute().strip()
        locale = self.locale.execute().strip() if self.locale else 'zh_CN'

        faker = Faker(locale=locale)
        generator = getattr(faker, generator)
        if not generator:
            logger.error('伪造函数不存在')
            return 'error'
        if generator.__code__.co_argcount > 1:
            logger.error('不支持带参数的伪造函数')
            return 'error'

        return generator()

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_min(params, 1)
        self.check_parameter_max(params, 2)
        # 提取参数
        self.provider = params[0]
        if len(params) > 1:
            self.locale = params[1]
