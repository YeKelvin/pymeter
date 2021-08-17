#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : random
# @Time    : 2020/1/20 16:06
# @Author  : Kelvin.Ye
import random
from typing import Final

from pymeter.functions.function import Function
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class Random(Function):

    REF_KEY: Final = '__Random'

    def __init__(self):
        self.length = None

    def execute(self):
        log.debug(f'start execute function:[ {self.REF_KEY} ]')

        if self.length == 1:
            length = int(self.length.execute().strip())
            result = ''.join([random.randint(0, 9) for x in range(length)])
            log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')
            return result

        result = str(random.random() * 8)
        log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')
        return result

    def set_parameters(self, params: list):
        log.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        self.check_parameter_min(params, 0)
        self.check_parameter_max(params, 1)

        if len(params) > 0:
            self.length = params[0]
