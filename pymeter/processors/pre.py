#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : pre.py
# @Time    : 2020/2/13 13:05
# @Author  : Kelvin.Ye
from pymeter.elements.element import TestElement


class PreProcessor(TestElement):
    def process(self) -> None:
        raise NotImplementedError
