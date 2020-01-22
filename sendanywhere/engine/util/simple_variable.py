#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : simple_variable
# @Time    : 2020/1/21 14:56
# @Author  : Kelvin.Ye


class SimpleVariable:
    def __init__(self, name: str = None):
        self.name = name

    @property
    def value(self):
        variables = self.get_variables()
        if self.name in variables:
            return variables.get(self.name)
        else:
            return '${' + self.name + '}'

    def get_variables(self):
        return {'varKey11': 'actual value11', 'varKey22': 'actual value22', 'varKey33': 'actual value33'}
