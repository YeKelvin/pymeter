#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : transaction_controller.py
# @Time    : 2021-08-24 23:23:12
# @Author  : Kelvin.Ye
from pymeter.controls.controller import Controller
from pymeter.controls.generic_controller import GenericController
from pymeter.samplers.transaction_sampler import TransactionSampler
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class TransactionController(GenericController):

    def __init__(self):
        self.transaction_sampler = None

    def next(self):
        """@Override"""
        return self.next_with_transaction_sampler()

    def next_with_transaction_sampler(self):
        # Check if transaction is done
        if self.transaction_sampler and self.transaction_sampler.transaction_done:
            log.debug(f'End of transaction {self.name}')

            # This transaction is done
            self.transaction_sampler = None
            return

        # Check if it is the start of a new transaction
        if self.first:  # must be the start of the subtree
            log.debug(f'Start of transaction {self.name}')
            self.transaction_sampler = TransactionSampler(self, self.name)

        # Sample the children of the transaction
        sub_sampler = super.next()
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
