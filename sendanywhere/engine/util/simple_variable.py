#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : simple_variable
# @Time    : 2020/1/21 14:56
# @Author  : Kelvin.Ye
from sendanywhere.coroutines.context import ContextService


class SimpleVariable:
    def __init__(self, name: str = None):
        self.name = name

    @property
    def variables(self):
        return ContextService.get_context().variables

    @property
    def value(self):
        if self.name in self.variables:
            return self.variables.get(self.name)
        else:
            return '${' + self.name + '}'
