#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : flask_db_iteration_storage.py
# @Time    : 2022/1/28 16:17
# @Author  : Kelvin.Ye
import importlib
from typing import Final

from pymeter.elements.element import TestElement
from pymeter.engine.interface import NoCoroutineClone
from pymeter.engine.interface import SampleListener
from pymeter.engine.interface import TestCollectionListener
from pymeter.groups.context import ContextService
from pymeter.samplers.sample_result import SampleResult


class FlaskDBIterationStorage(TestElement, TestCollectionListener, SampleListener, NoCoroutineClone):

    # 执行记录编号
    EXECUTION_NO: Final = 'FlaskDBIterationStorage__execution_no'

    # 测试集合编号
    COLLECTION_NO: Final = 'FlaskDBIterationStorage__collection_no'

    @property
    def execution_no(self):
        return self.get_property_as_str(self.EXECUTION_NO)

    @property
    def collection_no(self):
        return self.get_property_as_str(self.COLLECTION_NO)

    @property
    def last_sample_ok(self) -> bool:
        return ContextService.get_context().variables.get('Coroutine__last_sample_ok')

    def __init__(self):
        TestElement.__init__(self)
        self.flask_instance = getattr(importlib.import_module('app'), '__app__')
        self.table_model = importlib.import_module('app.script.model')
        self.TTestplanExecutionItems = self.table_model.TTestplanExecutionItems  # noqa
        self.success: bool = True

    def collection_started(self) -> None:
        """@override"""
        ...

    def collection_ended(self) -> None:
        """@override"""
        with self.flask_instance.app_context():
            if self.success:
                self.TTestplanExecutionItems.filter_by(
                    EXECUTION_NO=self.execution_no,
                    COLLECTION_NO=self.collection_no
                ).update({
                    'ITERATION_COUNT': self.TTestplanExecutionItems.ITERATION_COUNT + 1,
                    'SUCCESS_COUNT': self.TTestplanExecutionItems.SUCCESS_COUNT + 1,
                    'UPDATED_BY': 'PyMeter'
                })
            else:
                self.TTestplanExecutionItems.filter_by(
                    EXECUTION_NO=self.execution_no,
                    COLLECTION_NO=self.collection_no
                ).update({
                    'ITERATION_COUNT': self.TTestplanExecutionItems.ITERATION_COUNT + 1,
                    'FAILURE_COUNT': self.TTestplanExecutionItems.FAILURE_COUNT + 1,
                    'UPDATED_BY': 'PyMeter'
                })

    def sample_occurred(self, result: SampleResult) -> None:
        """@override"""
        # 最后一个 Sample 失败时，同步更新 Group/Collection 的结果也为失败
        if not self.last_sample_ok:
            self.success = False

    def sample_started(self, sample) -> None:
        """@override"""
        pass

    def sample_ended(self, result: SampleResult) -> None:
        """@override"""
        pass
