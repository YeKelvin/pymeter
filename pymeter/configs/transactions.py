#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : transaction.py
# @Time    : 2021/9/29 16:20
# @Author  : Kelvin.Ye
import requests

from pymeter.configs.arguments import Arguments
from pymeter.configs.httpconfigs import SessionManager
from pymeter.engine.interface import NoConfigMerge
from pymeter.engine.interface import TransactionConfig
from pymeter.engine.interface import TransactionListener
from pymeter.groups.context import ContextService
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class TransactionParameter(Arguments, TransactionConfig, NoConfigMerge, TransactionListener):

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


class TransactionHTTPSessionManager(SessionManager, TransactionConfig, TransactionListener):

    def __init__(self):
        super().__init__()

    def transaction_started(self) -> None:
        """@override"""
        log.debug('open new http session')
        self.session = requests.session()

    def transaction_ended(self) -> None:
        """@override"""
        log.debug(f'close http session:[ {self.session} ]')
        self.session.close()
