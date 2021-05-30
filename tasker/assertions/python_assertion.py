#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : python_assertion.py.py
# @Time    : 2020/2/17 16:39
# @Author  : Kelvin.Ye
from tasker.assertions.assertion import Assertion
from tasker.assertions.assertion import AssertionResult
from tasker.elements.element import TaskElement
from tasker.samplers.sample_result import SampleResult
from tasker.utils.log_util import get_logger


log = get_logger(__name__)


class PythonAssertion(Assertion, TaskElement):
    SOURCE = 'PythonAssertion__source'

    def get_result(self, response: SampleResult) -> AssertionResult:
        pass
