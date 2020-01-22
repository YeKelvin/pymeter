#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : eval
# @Time    : 2020/1/20 16:08
# @Author  : Kelvin.Ye
from sendanywhere.engine.util import CompoundVariable
from sendanywhere.functions.function import Function
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class Eval(Function):
    REF_KEY = '__Eval'

    def __init__(self):
        self.parameters = None

    def execute(self):
        log.debug(f'{self.REF_KEY} start execute')
        parameter = self.parameter.execute().strip()
        return CompoundVariable(parameter).execute().strip()

    def set_parameters(self, parameters: []):
        log.debug(f'{self.REF_KEY} start to set parameters')
        self.parameter = parameters[0]
