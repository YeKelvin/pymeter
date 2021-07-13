#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : post.py
# @Time    : 2020/2/13 13:06
# @Author  : Kelvin.Ye
from pymeter.elements.element import TestElement


class PostProcessor(TestElement):
    def process(self) -> None:
        raise NotImplementedError
