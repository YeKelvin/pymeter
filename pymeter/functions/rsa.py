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


class Random(Function):

    REF_KEY: Final = '__RSA'

    def __init__(self):
        self.plaintext = None
        self.public_key = None

    def execute(self):
        log.debug(f'start execute function:[ {self.REF_KEY} ]')

        plaintext = self.plaintext.execute().strip()
        public_key = self.plaintext.execute().strip()

        result = rsa_util.encrypt_by_public_key(plaintext, public_key)
        log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        log.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        # 校验函数参数个数
        self.check_parameter_count(params, 2)

        self.plaintext = params[0]
        self.public_key = params[1]
