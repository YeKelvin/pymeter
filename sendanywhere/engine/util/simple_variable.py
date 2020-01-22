#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : simple_variable
# @Time    : 2020/1/21 14:56
# @Author  : Kelvin.Ye


class SimpleVariable:
    def __init__(self, name: str = None):
        self.name = name

    def __str__(self):
        vars = self.get_variables()
        if vars:
            return vars.get(self.name)
        else:
            return '${' + self.name + '}'

    def get_variables(self):
        return {}
