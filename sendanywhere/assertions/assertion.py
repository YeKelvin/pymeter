#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : assertion.py
# @Time    : 2020/2/17 16:38
# @Author  : Kelvin.Ye
from sendanywhere.samplers.sample_result import SampleResult


class AssertionResult:
    def __init__(self):
        # Name of the assertion.
        self.name = None
        # True if the assertion failed.
        self.failure = False
        # True if there was an error checking the assertion.
        self.error = False
        # A message describing the failure.
        self.failure_message = None


class Assertion:
    def get_result(self, response: SampleResult) -> AssertionResult:
        raise NotImplementedError
