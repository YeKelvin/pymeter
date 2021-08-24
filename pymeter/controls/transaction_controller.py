#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : transaction_controller.py
# @Time    : 2021-08-24 23:23:12
# @Author  : Kelvin.Ye
from pymeter.controls.generic_controller import GenericController
from pymeter.samplers.sample_result import SampleResult
from pymeter.samplers.transaction_sampler import TransactionSampler
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class TransactionController(GenericController):

    def __init__(self):
        self.transaction_sampler = None

    def next(self):
        return self.next_with_transaction_sampler()

    def next_with_transaction_sampler(self):
        # Check if transaction is done
        if self.transaction_sampler and self.transaction_sampler.isTransactionDone():
            log.debug(f'End of transaction {self.name}')

            # This transaction is done
            self.transaction_sampler = None
            return

        # Check if it is the start of a new transaction
        if isFirst():  # must be the start of the subtree
            log.debug(f'Start of transaction {self.name}')
            self.transaction_sampler = TransactionSampler(self, self.name)

        # Sample the children of the transaction
        sub_sampler = super.next()
        self.transaction_sampler.setSubSampler(sub_sampler)

        # If we do not get any sub samplers, the transaction is done
        if (subSampler == null):
            self.transaction_sampler.setTransactionDone()

        return self.transaction_sampler

    def next_is_controller(self, controller: Controller):
        if (!isGenerateParentSample()) {
            return super.nextIsAController(controller);
        }
        Sampler returnValue;
        Sampler sampler = controller.next();
        if (sampler == null) {
            currentReturnedNull(controller);
            // We need to call the super.next, instead of this.next, which is done in GenericController,
            // because if we call this.next(), it will return the TransactionSampler, and we do not want that.
            // We need to get the next real sampler or controller
            returnValue = super.next();
        } else {
            returnValue = sampler;
        }
        return returnValue
