#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : transaction.py
# @Time    : 2021-08-24 23:23:12
# @Author  : Kelvin.Ye
from pymeter.controls.controller import Controller
from pymeter.controls.generic_controller import GenericController
from pymeter.samplers.sample_result import SampleResult
from pymeter.samplers.sampler import Sampler
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class TransactionController(GenericController):

    def __init__(self):
        super().__init__()
        self.transaction_sampler = None  # type: TransactionSampler

    def next(self):
        """@Override"""
        log.debug('start to get next sampler')
        next_sampler = self.next_with_transaction_sampler()
        log.debug(f'nextSampler:[ {next_sampler} ]')
        return next_sampler

    def next_with_transaction_sampler(self):
        # Check if transaction is done
        if self.transaction_sampler and self.transaction_sampler.transaction_done:
            log.debug(f'End of transaction:[ {self.name} ]')

            # This transaction is done
            self.transaction_sampler = None
            return

        # Check if it is the start of a new transaction
        if self.first:  # must be the start of the subtree
            log.debug(f'Start of transaction:[ {self.name} ]')
            self.transaction_sampler = TransactionSampler(self, self.name)

        # Sample the children of the transaction
        sub_sampler = super().next()
        self.transaction_sampler.sub_sampler = sub_sampler

        # If we do not get any sub samplers, the transaction is done
        if sub_sampler is None:
            self.transaction_sampler.set_transaction_done()

        return self.transaction_sampler

    def next_is_controller(self, controller: Controller):
        """@Override"""
        sampler = controller.next()
        if sampler is None:
            self.current_returned_none(controller)
            # We need to call the super.next, instead of this.next, which is done in GenericController,
            # because if we call this.next(), it will return the TransactionSampler, and we do not want that.
            # We need to get the next real sampler or controller
            return super().next()
        else:
            return sampler

    def trigger_end_of_loop(self):
        """@Override"""
        sub_sampler = self.transaction_sampler.sub_sampler
        # triggerEndOfLoop is called when error occurs to end Main Loop
        # in this case normal workflow doesn't happen, so we need
        # to notify the children of TransactionController and
        # update them with SubSamplerResult
        if isinstance(sub_sampler, TransactionSampler):
            self.transaction_sampler.add_sub_sampler_result(sub_sampler.transaction_sample_result)

        self.transaction_sampler.set_transaction_done()
        # This transaction is done
        self.transaction_sampler = None

        super().triggerEndOfLoop()


class TransactionSampler(Sampler):

    def __init__(self, controller: TransactionController, name: str):
        super().__init__(name)
        self.transaction_controller = controller

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
            f'Number of samples in transaction:[ {self.calls} ], number of failing samples:[ {self.no_failing_samples} ]')

        if self.transaction_sample_result.success:
            self.transaction_sample_result.response_code = 200
