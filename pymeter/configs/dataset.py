#!/usr/bin python3
# @File    : dataset.py
# @Time    : 2021-08-02 17:28:54
# @Author  : Kelvin.Ye
from loguru import logger

from pymeter.configs.arguments import Arguments
from pymeter.engines.interface import NoConfigMerge
from pymeter.engines.interface import NoThreadClone
from pymeter.engines.interface import TestCollectionListener
from pymeter.workers.context import ContextService


class VariableDataset(Arguments, TestCollectionListener, NoConfigMerge, NoThreadClone):

    def collection_started(self) -> None:
        """@override"""
        logger.debug('开始加载变量集')
        variables = ContextService.get_context().variables
        for key, value in self.to_dict().items():
            if not key:
                continue
            variables.put(key, value)

    def collection_ended(self) -> None:
        """@override"""
        ...
