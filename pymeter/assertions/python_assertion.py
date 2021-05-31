#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_assertion.py.py
# @Time    : 2020/2/17 16:39
# @Author  : Kelvin.Ye
from pymeter.assertions.assertion import Assertion
from pymeter.assertions.assertion import AssertionResult
from pymeter.elements.element import TestElement
from pymeter.samplers.sample_result import SampleResult
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class PythonAssertion(Assertion, TestElement):
    SOURCE = 'PythonAssertion__source'

    def get_result(self, response: SampleResult) -> AssertionResult:
        pass
