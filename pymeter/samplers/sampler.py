#!/usr/bin python3
# @File    : sampler.py
# @Time    : 2020/1/24 23:47
# @Author  : Kelvin.Ye
from pymeter.elements.element import TestElement


class Sampler(TestElement):

    def sample(self):
        raise NotImplementedError
