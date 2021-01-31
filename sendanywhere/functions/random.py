#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : random
# @Time    : 2020/1/20 16:06
# @Author  : Kelvin.Ye
import random
from typing import Final

from sendanywhere.coroutines.context import ContextService
from sendanywhere.functions.function import Function
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class Random(Function):
    REF_KEY: Final = '__Random'

    def __init__(self):
        self.var_name = None
        self.length = None
        self.minimum = None
        self.maximum = None

    def execute(self):
        log.debug(f'{self.REF_KEY} start execute')
        minimum = int(self.minimum.execute().strip())
        maximum = int(self.maximum.execute().strip())

        result = random.randint(minimum, maximum)

        if self.var_name:
            # 存在 var_name时放入本地变量中
            var_name = self.var_name.execute().strip()
            ContextService.get_context().variables.put(var_name, result)

        return str(result)

    def set_parameters(self, parameters: list):
        log.debug(f'{self.REF_KEY} start to set parameters')
        self.minimum = parameters[0]
        self.maximum = parameters[1]
        if len(parameters) > 2:
            self.var_name = parameters[2]
