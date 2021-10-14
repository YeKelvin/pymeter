#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : timer
# @Time    : 2020/2/29 17:03
# @Author  : Kelvin.Ye
from pymeter.elements.element import TestElement


class Timer(TestElement):

    def delay(self):
        raise NotImplementedError
