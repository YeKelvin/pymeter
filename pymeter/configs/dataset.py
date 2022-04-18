#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : dataset.py
# @Time    : 2021-08-02 17:28:54
# @Author  : Kelvin.Ye
from pymeter.configs.arguments import Arguments
from pymeter.engine.interface import NoConfigMerge
from pymeter.engine.interface import NoCoroutineClone
from pymeter.engine.interface import TestCollectionListener
from pymeter.groups.context import ContextService
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class VariableDataset(Arguments, TestCollectionListener, NoConfigMerge, NoCoroutineClone):

    def collection_started(self) -> None:
        """@override"""
        log.debug('start to load dataset')
        variables = ContextService.get_context().variables
        for key, value in self.to_dict().items():
            if not key:
                continue
            variables.put(key, value)

    def collection_ended(self) -> None:
        """@override"""
        ...
