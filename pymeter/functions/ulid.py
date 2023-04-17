#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : random.py
# @Time    : 2020/1/20 16:06
# @Author  : Kelvin.Ye
from typing import Final

from loguru import logger
from ulid import microsecond as ulid

from pymeter.functions.function import Function


class ULID(Function):

    REF_KEY: Final = '__ULID'

    def execute(self):
        logger.debug(f'start execute function:[ {self.REF_KEY} ]')

        result = ulid.new().str
        logger.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')
        return result

    def set_parameters(self, params: list):
        logger.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        # 校验函数参数个数
        self.check_parameter_count(params, 0)
