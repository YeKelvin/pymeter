#!/usr/bin python3
# @File    : md5.py
# @Time    : 2021-08-17 17:37:04
# @Author  : Kelvin.Ye
import hashlib
from typing import Final

from loguru import logger

from pymeter.functions.function import Function


class MD5(Function):

    REF_KEY: Final = '__md5'

    def __init__(self):
        self.data = None
        self.encoding = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')

        data = self.data.execute().strip()
        encoding = self.encoding.execute().strip() if self.encoding else 'UTF-8'

        return hashlib.md5(data.encode(encoding=encoding)).hexdigest()

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_min(params, 1)
        # 提取参数
        self.data = params[0]
        self.encoding = params[1] if len(params) > 1 else None
