#!/usr/bin python3
# @File    : aes.py
# @Time    : 2022/10/12 18:21
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger

from pymeter.functions.function import Function
from pymeter.utils import aes_util as aes_cryptor


class AES(Function):

    REF_KEY: Final = '__aes'

    def __init__(self):
        self.data = None
        self.key = None
        self.mode = None
        self.size = None
        self.iv = None
        self.encoding = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')

        data = self.data.execute().strip()
        key = self.key.execute().strip()
        mode = self.mode.execute().strip()
        size = self.size.execute().strip()
        iv = self.iv.execute().strip() or None if self.iv else None
        encoding = self.encoding.execute().strip() if self.encoding else 'base64'

        return aes_cryptor.encrypt(data, key, mode, size, iv, encoding)

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_min(params, 4)
        self.check_parameter_max(params, 5)
        # 提取参数
        self.data = params[0]
        self.key = params[1]
        self.mode = params[2]
        self.size = params[3]
        self.iv = params[4] if len(params) > 4 else None
        self.encoding = params[5] if len(params) > 5 else None
