#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : random_choice.py
# @Time    : 2021-08-18 09:13:37
# @Author  : Kelvin.Ye
import random
from typing import Final

from pymeter.functions.function import Function
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class RandomChoice(Function):

    REF_KEY: Final = '__RandomChoice'

    def __init__(self):
        self.seq = None

    def execute(self):
        log.debug(f'start execute function:[ {self.REF_KEY} ]')

        seq = self.seq.execute().strip().split(',')
        seq = [s.strip() for s in seq]

        result = str(random.choice(seq))
        log.debug(f'function:[ {self.REF_KEY} ] result:[ {result} ]')

        return result

    def set_parameters(self, params: list):
        log.debug(f'start to set function parameters:[ {self.REF_KEY} ]')

        self.check_parameter_count(params, 1)
        self.seq = params[0]
