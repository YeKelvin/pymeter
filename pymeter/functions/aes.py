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
        self.plaintext = None
        self.key = None
        self.block_size = None
        self.mode = None
        self.iv = None
        self.encoding = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')

        plaintext = self.plaintext.execute().strip()
        key = self.key.execute().strip()
        block_size = self.block_size.execute().strip() if self.block_size else '128'
        mode = self.mode.execute().strip() if self.mode else 'ECB'
        iv = self.iv.execute().strip() or None if self.iv else None
        encoding = self.encoding.execute().strip() if self.encoding else 'base64'

        return aes_cryptor.encrypt(plaintext, key, block_size, mode, iv, encoding)

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_min(params, 2)
        self.check_parameter_max(params, 5)
        # 提取参数
        self.plaintext = params[0]
        self.key = params[1]
        self.block_size = params[2] if len(params) > 2 else None
        self.mode = params[3] if len(params) > 3 else None
        self.iv = params[4] if len(params) > 4 else None
        self.encoding = params[5] if len(params) > 5 else None
