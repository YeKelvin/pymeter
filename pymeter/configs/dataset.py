#!/usr/bin python3
# @File    : dataset.py
# @Time    : 2021-08-02 17:28:54
# @Author  : Kelvin.Ye
from loguru import logger

from pymeter.configs.arguments import Arguments
from pymeter.engine.interface import NoConfigMerge
from pymeter.engine.interface import NoThreadClone
from pymeter.engine.interface import TestCollectionListener
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
