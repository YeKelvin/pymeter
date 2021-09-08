#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : rsa.py
# @Time    : 2021-08-17 17:37:01
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.functions.function import Function
from pymeter.utils import rsa_util
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class RSA(Function):

    REF_KEY: Final = '__RSA'
    PUBLIC_KEY_PREFIX = '-----BEGIN RSA PUBLIC KEY-----\n'
    PUBLIC_KEY_SUFFIX = '\n-----END RSA PUBLIC KEY-----'

    def __init__(self):
        self.plaintext = None
        self.public_key = None

    def execute(self):
        log.debug(f'start execute function:[ {self.REF_KEY} ]')

        plaintext = self.plaintext.execute().strip()
        public_key = self.public_key.execute().strip()

        if not public_key.startswith(RSA.PUBLIC_KEY_PREFIX):
            public_key = RSA.PUBLIC_KEY_PREFIX + public_key

        if not public_key.endswith(RSA.PUBLIC_KEY_SUFFIX):
            public_key = public_key + RSA.PUBLIC_KEY_SUFFIX

        log.debug(f'public_key:\n{public_key}')
        result = rsa_util.encrypt_by_public_key(plaintext, public_key).decode(encoding='UTF-8')
        log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        log.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        # 校验函数参数个数
        self.check_parameter_count(params, 2)

        self.plaintext = params[0]
        self.public_key = params[1]
