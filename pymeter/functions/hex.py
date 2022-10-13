#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : hex.py
# @Time    : 2022/10/13 17:19
# @Author  : Kelvin.Ye
import binascii
from typing import Final

from pymeter.functions.function import Function
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class Hex(Function):

    REF_KEY: Final = '__HEX'

    def __init__(self):
        self.data = None

    def execute(self):
        log.debug(f'start execute function:[ {self.REF_KEY} ]')

        data = self.data.execute().strip()

        result = binascii.b2a_hex(data).decode('utf8')
        log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        log.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        # 校验函数参数个数
        self.check_parameter_count(params, 1)
        # 提取参数
        self.data = params[0]
