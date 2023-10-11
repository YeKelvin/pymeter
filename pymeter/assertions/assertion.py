#!/usr/bin python3
# @File    : assertion.py
# @Time    : 2020/2/17 16:38
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.elements.element import TestElement
from pymeter.samplers.sample_result import SampleResult


class AssertionResult:

    def __init__(self, name: str = None):
        self.name = name
        self.message = None
        self.error = False
        self.failure = False

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.__dict__.__str__()


class Assertion(TestElement):

    TYPE: Final = 'ASSERT'

    def get_result(self, result: SampleResult) -> AssertionResult:
        raise NotImplementedError
