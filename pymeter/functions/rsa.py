#!/usr/bin python3
# @File    : rsa.py
# @Time    : 2021-08-17 17:37:01
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger

from pymeter.functions.function import Function
from pymeter.utils import rsa_util as rsa_cryptor


class RSA(Function):

    REF_KEY: Final = '__rsa'
    PUBLIC_KEY_PREFIX = '-----BEGIN RSA PUBLIC KEY-----\n'
    PUBLIC_KEY_SUFFIX = '\n-----END RSA PUBLIC KEY-----'

    def __init__(self):
        self.plaintext = None
        self.public_key = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')

        plaintext = self.plaintext.execute().strip()
        public_key = self.public_key.execute().strip()

        if not public_key.startswith(RSA.PUBLIC_KEY_PREFIX):
            public_key = RSA.PUBLIC_KEY_PREFIX + public_key

        if not public_key.endswith(RSA.PUBLIC_KEY_SUFFIX):
            public_key = public_key + RSA.PUBLIC_KEY_SUFFIX

        return rsa_cryptor.encrypt_by_public_key(plaintext, public_key).decode(encoding='UTF-8')

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_count(params, 2)
        # 提取参数
        self.plaintext = params[0]
        self.public_key = params[1]
