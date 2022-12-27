#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : aes.py
# @Time    : 2022/10/12 18:21
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.functions.function import Function
from pymeter.utils import aes_util as aes_cryptor
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class AES(Function):

    REF_KEY: Final = '__AES128ECB'

    def __init__(self):
        self.plaintext = None
        self.key = None

    def execute(self):
        log.debug(f'start execute function:[ {self.REF_KEY} ]')

        plaintext = self.plaintext.execute().strip()
        key = self.key.execute().strip()

        result = aes_cryptor.encrypt(plaintext, key, '16', 'ECB', 'base64')
        log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        log.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        # 校验函数参数个数
        self.check_parameter_count(params, 2)
        # 提取参数
        self.plaintext = params[0]
        self.key = params[1]
