#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : assertion.py
# @Time    : 2020/2/17 16:38
# @Author  : Kelvin.Ye
from pymeter.elements.element import TestElement
from pymeter.samplers.sample_result import SampleResult


class AssertionResult:

    def __init__(self, name: str = None):
        # Name of the assertion.
        self.name = name

        # True if the assertion failed.
        self.failure = False

        # True if there was an error checking the assertion.
        self.error = False

        # A message describing the failure or error.
        self.message = None

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.__dict__.__str__()


class Assertion(TestElement):

    def get_result(self, result: SampleResult) -> AssertionResult:
        raise NotImplementedError
