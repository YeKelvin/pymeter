#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : transaction_parameter.py
# @Time    : 2021/9/29 16:20
# @Author  : Kelvin.Ye
from pymeter.configs.arguments import TransactionArguments
from pymeter.engine.interface import NoConfigMerge
from pymeter.engine.interface import TransactionListener
from pymeter.groups.context import ContextService
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class TransactionParameter(TransactionArguments, TransactionListener, NoConfigMerge):

    def transaction_started(self) -> None:
        """@override"""
        variables = ContextService.get_context().variables
        for key, value in self.to_dict().items():
            if not key:
                continue
            variables.put(key, value)

    def transaction_ended(self) -> None:
        """@override"""
        ...
