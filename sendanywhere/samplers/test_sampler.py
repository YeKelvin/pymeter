#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_sampler
# @Time    : 2020/3/3 17:58
# @Author  : Kelvin.Ye
from sendanywhere.samplers.sample_result import SampleResult
from sendanywhere.samplers.sampler import Sampler
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class TestSampler(Sampler, TestElement):
    SAMPLER_DATA = 'sampler_data'
    EXPECTED_SUCCESS = 'expected_success'

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
        result.response_data = self.sampler_data
        result.success = self.expected_success
        result.sample_end()

        return result
