#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_sampler
# @Time    : 2020/3/3 17:58
# @Author  : Kelvin.Ye
from typing import Final

import gevent

from taskmeter.elements.element import TestElement
from taskmeter.samplers.sample_result import SampleResult
from taskmeter.samplers.sampler import Sampler
from taskmeter.utils.log_util import get_logger


log = get_logger(__name__)


class TestSampler(Sampler, TestElement):
    SAMPLER_DATA: Final = 'TestSampler__sampler_data'
    EXPECTED_SUCCESS: Final = 'TestSampler__expected_success'

    @property
    def sampler_data(self):
        return self.get_property_as_str(self.SAMPLER_DATA)

    @property
    def expected_success(self):
        return self.get_property_as_bool(self.EXPECTED_SUCCESS)

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_label = self.get_property_as_str(self.LABEL)
        result.request_body = self.sampler_data
        result.sample_start()
        gevent.sleep(0.5)
        result.sample_end()
        result.success = self.expected_success
        result.response_data = self.sampler_data
        result.calculate_elapsed_time()

        return result
