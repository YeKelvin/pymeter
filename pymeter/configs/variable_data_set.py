#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : variable_data_set.py
# @Time    : 2021-08-02 17:28:54
# @Author  : Kelvin.Ye
from pymeter.configs.arguments import Arguments
from pymeter.elements.interface import NoConfigMerge
from pymeter.engine.interface import TestCollectionListener
from pymeter.groups.context import ContextService
from pymeter.groups.interface import NoCoroutineClone


class VariableDataSet(Arguments, TestCollectionListener, NoConfigMerge, NoCoroutineClone):

    def collection_started(self) -> None:
        """@override"""
        variables = ContextService.get_context().variables
        for key, value in self.to_dict().items():
            if not key:
                continue
            variables.put(key, value)

    def collection_ended(self) -> None:
        """@override"""
        ...
