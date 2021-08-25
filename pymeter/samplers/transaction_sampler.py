#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : transaction_sampler.py
# @Time    : 2021-08-24 23:41:09
# @Author  : Kelvin.Ye
from pymeter.samplers.sample_result import SampleResult
from pymeter.samplers.sampler import Sampler
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class TransactionSampler(Sampler):

    def __init__(self, controller, name):
        self.transaction_controller = controller
        self.name = name

        self.transaction_done = False
        self.sub_sampler = None

        self.calls = 0
        self.no_failing_samples = 0
        self.total_time = 0

        self.transaction_sample_result = SampleResult()
        self.transaction_sample_result.sample_name = name
        self.transaction_sample_result.success = True
        self.transaction_sample_result.sample_start()

    def add_sub_sampler_result(self, result: SampleResult):
        # Another subsample for the transaction
        self.calls += 1

        # Set Response code of transaction
        if self.no_failing_samples == 0:
            self.transaction_sample_result.response_code = result.response_code

        # The transaction fails if any sub sample fails
        if not result.success:
            self.transaction_sample_result.success = False
            self.no_failing_samples += 1

        # Add the sub result to the transaction result
        self.transaction_sample_result.add_sub_result(result)
        # Add current time to total for later use (exclude pause time)
        self.total_time += (result.end_time - result.start_time - result.idle_time)

    def set_transaction_done(self):
        self.transaction_done = True
        # Set the overall status for the transaction sample
        self.transaction_sample_result.response_message = (
            f'Number of samples in transaction : {self.calls}, number of failing samples : {self.no_failing_samples}')

        if self.transaction_sample_result.success:
            self.transaction_sample_result.response_code = 200
