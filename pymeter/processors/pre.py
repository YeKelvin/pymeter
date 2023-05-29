#!/usr/bin python3
# @File    : pre.py
# @Time    : 2020/2/13 13:05
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.elements.element import TestElement


class PreProcessor(TestElement):

    TYPE: Final = 'PRE'

    def process(self) -> None:
        raise NotImplementedError
