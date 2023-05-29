#!/usr/bin python3
# @File    : post.py
# @Time    : 2020/2/13 13:06
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.elements.element import TestElement


class PostProcessor(TestElement):

    TYPE: Final = 'POST'

    def process(self) -> None:
        raise NotImplementedError
