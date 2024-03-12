#!/usr/bin python3
# @File    : rsa.py
# @Time    : 2021-08-17 17:37:01
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger

from pymeter.functions.function import Function
from pymeter.utils import rsa_util


class RSA(Function):

    REF_KEY: Final = '__rsa'
    PUBLIC_KEY_PREFIX = '-----BEGIN RSA PUBLIC KEY-----\n'
    PUBLIC_KEY_SUFFIX = '\n-----END RSA PUBLIC KEY-----'

    def __init__(self):
        self.data = None
        self.public_key = None

    def execute(self):
        logger.debug(f'执行函数:[ {self.REF_KEY} ]')

        data = self.data.execute().strip()
        public_key = self.public_key.execute().strip()

        if 'RSA PUBLIC KEY' not in public_key:
            public_key = RSA.PUBLIC_KEY_PREFIX + public_key + RSA.PUBLIC_KEY_SUFFIX

        return rsa_util.encrypt_by_public_key(data, public_key)

    def set_parameters(self, params: list):
        # 校验函数实参数量
        self.check_parameter_count(params, 2)
        # 提取参数
        self.data = params[0]
        self.public_key = params[1]
