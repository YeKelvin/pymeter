#!/usr/bin python3
# @File    : prev.py
# @Time    : 2020/2/13 13:05
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.elements.element import TestElement


class PrevProcessor(TestElement):

    TYPE: Final = 'PREV'

    def process(self) -> None:
        raise NotImplementedError
