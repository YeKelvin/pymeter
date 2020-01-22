#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : eval
# @Time    : 2020/1/20 16:08
# @Author  : Kelvin.Ye
from sendanywhere.functions.function import Function
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class Eval(Function):
    REF_KEY = '__eval'

    def execute(self):
        pass

    def set_parameters(self, parameters: []):
        pass
