#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : md5.py
# @Time    : 2021-08-17 17:37:04
# @Author  : Kelvin.Ye
import hashlib
from typing import Final

from pymeter.functions.function import Function
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class Random(Function):

    REF_KEY: Final = '__MD5'

    def __init__(self):
        self.plaintext = None
        self.encode = None

    def execute(self):
        log.debug(f'start execute function:[ {self.REF_KEY} ]')

        plaintext = self.plaintext.execute().strip()
        encode = 'UTF-8'

        if self.encode:
            encode = self.encode.execute().strip()

        result = hashlib.md5(plaintext.encode(encoding=encode)).hexdigest()
        log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        log.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        # 校验函数参数个数
        self.check_parameter_min(params, 1)

        self.plaintext = params[0]

        if len(params) > 1:
            self.encode = params[1]
