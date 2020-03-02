#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : assertion.py
# @Time    : 2020/2/17 16:38
# @Author  : Kelvin.Ye
from sendanywhere.samplers.sample_result import SampleResult


class AssertionResult:
    def __init__(self, name: str = None):
        # Name of the assertion.
        self.name = name
        # True if the assertion failed.
        self.is_failure = False
        # True if there was an error checking the assertion.
        self.is_error = False
        # A message describing the failure.
        self.failure_message = None


class Assertion:
    def get_result(self, result: SampleResult) -> AssertionResult:
        raise NotImplementedError
