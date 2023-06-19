#!/usr/bin python3
# @File    : md5.py
# @Time    : 2021-08-17 17:37:04
# @Author  : Kelvin.Ye
import hashlib
from typing import Final

from loguru import logger

from pymeter.functions.function import Function


class MD5(Function):

    REF_KEY: Final = '__MD5'

    def __init__(self):
        self.plaintext = None
        self.encode = None

    def execute(self):
        logger.debug(f'开始执行函数:[ {self.REF_KEY} ]')

        plaintext = self.plaintext.execute().strip()
        encode = self.encode.execute().strip() if self.encode else 'UTF-8'

        result = hashlib.md5(plaintext.encode(encoding=encode)).hexdigest()
        logger.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_min(params, 1)
        # 提取参数
        self.plaintext = params[0]
        self.encode = params[1] if len(params) > 1 else None
