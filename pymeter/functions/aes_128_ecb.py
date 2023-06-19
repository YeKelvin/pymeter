#!/usr/bin python3
# @File    : aes.py
# @Time    : 2022/10/12 18:21
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger

from pymeter.functions.function import Function
from pymeter.utils import aes_util as aes_cryptor


class AES128ECB(Function):

    REF_KEY: Final = '__AES128ECB'

    def __init__(self):
        self.plaintext = None
        self.key = None
        self.iv = None

    def execute(self):
        logger.debug(f'开始执行函数:[ {self.REF_KEY} ]')

        plaintext = self.plaintext.execute().strip()
        key = self.key.execute().strip()
        iv = self.iv.execute().strip() or None if self.iv else None

        result = aes_cryptor.encrypt(plaintext, key, size='128', mode='ECB', iv=iv, encoding='base64')
        logger.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_min(params, 2)
        self.check_parameter_max(params, 3)
        # 提取参数
        self.plaintext = params[0]
        self.key = params[1]
        self.iv = params[2] if len(params) > 2 else None
