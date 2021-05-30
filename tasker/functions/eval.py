#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : eval
# @Time    : 2020/1/20 16:08
# @Author  : Kelvin.Ye
from typing import Final

from tasker.engine import value_parser
from tasker.functions.function import Function
from tasker.utils.log_util import get_logger


log = get_logger(__name__)


class Eval(Function):
    REF_KEY: Final = '__Eval'

    def __init__(self):
        self.parameter = None

    def execute(self):
        log.debug(f'{self.REF_KEY} start execute')
        parameter = self.parameter.execute().strip()
        return value_parser.CompoundVariable(parameter).execute().strip()

    def set_parameters(self, parameters: list):
        log.debug(f'{self.REF_KEY} start to set parameters')
        self.parameter = parameters[0]
