#!/usr/bin python3
# @File    : google_auth.py
# @Time    : 2021-08-17 18:58:12
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger

from pymeter.functions.function import Function
from pymeter.utils.google_util import GoogleAuthenticate


class GoogleAuth(Function):

    REF_KEY: Final = '__google_auth'

    def __init__(self):
        self.secret_key = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')
        secret_key = self.secret_key.execute().strip()
        return str(GoogleAuthenticate.get_code(secret_key))

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_count(params, 1)
        # 提取参数
        self.secret_key = params[0]
