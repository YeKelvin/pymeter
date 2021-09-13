#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : flask_result_storage.py
# @Time    : 2021-09-09 21:17:33
# @Author  : Kelvin.Ye
import importlib
from datetime import datetime
from typing import Final

from pymeter.elements.element import TestElement
from pymeter.engine.interface import NoCoroutineClone
from pymeter.engine.interface import SampleListener
from pymeter.engine.interface import TestCollectionListener
from pymeter.engine.interface import TestGroupListener
from pymeter.engine.interface import TestIterationListener
from pymeter.groups.context import ContextService
from pymeter.samplers.sample_result import SampleResult
from pymeter.utils import time_util
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class FlaskDBResultStorage(
    TestElement, TestCollectionListener, TestGroupListener, SampleListener, TestIterationListener, NoCoroutineClone
):

    # 测试计划编号
    PLAN_NO: Final = 'FlaskDBResultStorage__plan_no'

    # 测试报告编号
    REPORT_NO: Final = 'FlaskDBResultStorage__report_no'

    # 测试集合编号
    COLLECTION_NO: Final = 'FlaskDBResultStorage__collection_no'

    @property
    def app(self):
        module = importlib.import_module('app')
        app = getattr(module, '__app__')
        return app

    @property
    def model(self):
        return importlib.import_module('app.script.model')

    @property
    def plan_no(self):
        return self.get_property_as_str(self.PLAN_NO)

    @property
    def report_no(self):
        return self.get_property_as_str(self.REPORT_NO)

    @property
    def collection_no(self):
        return self.get_property_as_str(self.COLLECTION_NO)

    @property
    def collection(self):
        return ContextService.get_context().engine.collection

    @property
    def collection_id(self):
        return id(self.collection)

    @property
    def group(self):
        return ContextService.get_context().group

    @property
    def group_id(self):
        return id(self.group)

    def __init__(self):
        TestElement.__init__(self)
        self.success: bool = True

    def collection_started(self) -> None:
        """@override"""
        # 记录 Collection 开始时间
        self.collection_start_time = time_util.timestamp_now()
        # 插入 Collection 数据至数据库
        self.insert_test_collection_result()

    def collection_ended(self) -> None:
        """@override"""
        # 记录 Collection 结束时间
        self.collection_end_time = time_util.timestamp_now()
        # 更新 Collection 数据
        self.update_test_collection_result()

    def group_started(self) -> None:
        """@override"""
        # 记录 Group 开始时间
        self.group.start_time = time_util.timestamp_now()
        # 插入 Group 数据至数据库
        self.insert_test_group_result()

    def group_finished(self) -> None:
        """@override"""
        # 记录 Group 结束时间
        self.group.end_time = time_util.timestamp_now()
        # 更新 Group 数据
        self.update_test_group_result()

    def sample_occurred(self, result: SampleResult) -> None:
        """@override"""
        # 插入 Sampler 数据至数据库
        self.insert_test_sampler_result(result)
        # 如果 Sample 失败，则同步更新 Group/Collection 的结果也为失败
        if not result.success:
            self.group.success = False
            if self.success:
                self.success = False

    def sample_started(self, sample) -> None:
        """@override"""
        pass

    def sample_ended(self, result: SampleResult) -> None:
        """@override"""
        pass

    def test_iteration_start(self, controller, iter) -> None:
        pass

    def insert_test_collection_result(self):
        log.debug('insert collection result')
        with self.app.app_context():
            self.model.TTestCollectionResult.insert(
                REPORT_NO=self.report_no,
                COLLECTION_NO=self.collection_no,
                COLLECTION_ID=self.collection_id,
                COLLECTION_NAME=self.collection.name,
                COLLECTION_REMARK=self.collection.remark,
                START_TIME=datetime.fromtimestamp(self.collection_start_time),
                SUCCESS=True,
                CREATED_BY='PyMeter',
                UPDATED_BY='PyMeter'
            )

    def insert_test_group_result(self):
        log.debug('insert group result')
        with self.app.app_context():
            self.model.TTestGroupResult.insert(
                REPORT_NO=self.report_no,
                COLLECTION_ID=self.collection_id,
                GROUP_ID=self.group_id,
                GROUP_NAME=self.group.name,
                GROUP_REMARK=self.group.remark,
                START_TIME=datetime.fromtimestamp(self.group.start_time),
                SUCCESS=True,
                CREATED_BY='PyMeter',
                UPDATED_BY='PyMeter'
            )

    def insert_test_sampler_result(self, result: SampleResult):
        log.debug('insert sampler result')
        err_assertion_data = None
        if result.assertions:
            assertions = [assertion for assertion in result.assertions if assertion.failure or assertion.error]
            if len(assertions) > 0:
                err_assertion_data = assertions[0].message

        with self.app.app_context():
            self.model.TTestSamplerResult.insert(
                REPORT_NO=self.report_no,
                GROUP_ID=self.group_id,
                PARENT_ID=id(result.parent) if result.parent else None,
                SAMPLER_ID=id(result),
                SAMPLER_NAME=result.sample_name,
                SAMPLER_REMARK=result.sample_remark,
                START_TIME=result.start_time,
                END_TIME=result.end_time,
                ELAPSED_TIME=result.elapsed_time,
                SUCCESS=result.success,
                REQUEST_URL=result.request_url,
                REQUEST_DATA=result.request_data,
                REQUEST_HEADERS=result.request_headers,
                RESPONSE_DATA=result.response_data,
                RESPONSE_HEADERS=result.response_headers,
                ERROR_ASSERTION=err_assertion_data,
                CREATED_BY='PyMeter',
                UPDATED_BY='PyMeter'
            )

    def update_test_collection_result(self):
        log.debug('update collection result')
        elapsed_time = int(self.collection_end_time * 1000) - int(self.collection_start_time * 1000)
        with self.app.app_context():
            self.model.TTestCollectionResult.query_by(COLLECTION_ID=self.collection_id).update(
                END_TIME=datetime.fromtimestamp(self.collection_end_time),
                ELAPSED_TIME=time_util.microsecond_to_m_s(elapsed_time),
                SUCCESS=self.success
            )

    def update_test_group_result(self):
        log.debug('update group result')
        success = getattr(self.group, 'success', True)
        elapsed_time = int(self.group.end_time * 1000) - int(self.group.start_time * 1000)
        with self.app.app_context():
            self.model.TTestGroupResult.query_by(GROUP_ID=self.group_id).update(
                END_TIME=datetime.fromtimestamp(self.group.end_time),
                ELAPSED_TIME=time_util.microsecond_to_m_s(elapsed_time),
                SUCCESS=success
            )
