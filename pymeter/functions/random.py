#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : random
# @Time    : 2020/1/20 16:06
# @Author  : Kelvin.Ye
import random
from typing import Final

from pymeter.functions.function import Function
from pymeter.utils import random_util
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class Random(Function):

    REF_KEY: Final = '__Random'

    def __init__(self):
        self.length = None
        self.minimum = None
        self.maximum = None
        self.params_count = 0

    def execute(self):
        log.debug(f'start execute function:[ {self.REF_KEY} ]')

        if self.params_count == 1:
            length = int(self.length.execute().strip())
            result = random_util.get_number(length)
            log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')
            return result

        if self.params_count == 2:
            minimum = int(self.minimum.execute().strip())
            maximum = int(self.maximum.execute().strip())
            result = str(random.randint(minimum, maximum))
            log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')
            return result

    def set_parameters(self, params: list):
        log.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        self.check_parameter_min(params, 1)
        self.check_parameter_max(params, 2)

        self.params_count = len(params)

        if self.params_count == 1:
            self.length = params[0]

        if self.params_count == 2:
            self.minimum = params[0]
            self.maximum = params[1]
