#!/usr/bin python3
# @File    : base64.py
# @Time    : 2022/10/12 18:31
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger

from pymeter.functions.function import Function
from pymeter.utils import base64_util


class Base64(Function):

    REF_KEY: Final = '__Base64'

    def __init__(self):
        self.data = None

    def execute(self):
        logger.debug(f'开始执行函数:[ {self.REF_KEY} ]')

        data = self.data.execute().strip()

        result = base64_util.encode(data)
        logger.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_count(params, 1)
        # 提取参数
        self.data = params[0]
