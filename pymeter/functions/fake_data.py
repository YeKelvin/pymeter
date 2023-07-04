#!/usr/bin python3
# @File    : fake_data.py
# @Time    : 2023-06-19 12:12:07
# @Author  : Kelvin.Ye
from typing import Final

from faker import Faker
from loguru import logger

from pymeter.functions.function import Function
from pymeter.tools.exceptions import FunctionExecutionError


class FakeData(Function):

    REF_KEY: Final = '__Faker'

    def __init__(self):
        self.locale = None
        self.generator = None
        self.generator_params = []

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')
        generator = self.generator.execute().strip()
        locale = self.locale.execute().strip() if self.locale else 'zh_CN'
        params = [param.execute().strip() for param in self.generator_params]

        faker = Faker(locale=locale)
        if fakefn := getattr(faker, generator):
            return fakefn(*params) if params else fakefn()
        else:
            raise FunctionExecutionError('不存在的伪造类型')

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_min(params, 1)
        # 提取参数
        self.generator = params[0]
        if len(params) > 1:
            self.locale = params[1]
        if len(params) > 2:
            self.generator_params = params[2:]
