#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : flask_db_result_storage.py
# @Time    : 2021-09-09 21:17:33
# @Author  : Kelvin.Ye
import importlib
from typing import Final

from loguru import logger

from pymeter.elements.element import TestElement
from pymeter.engine.interface import NoCoroutineClone
from pymeter.engine.interface import SampleListener
from pymeter.engine.interface import TestCollectionListener
from pymeter.engine.interface import TestGroupListener
from pymeter.groups.context import ContextService
from pymeter.samplers.sample_result import SampleResult
from pymeter.utils.json_util import to_json
from pymeter.utils.time_util import timestamp_now
from pymeter.utils.time_util import timestmp_to_utc8_datetime


class FlaskDBResultStorage(TestElement, TestCollectionListener, TestGroupListener, SampleListener, NoCoroutineClone):

    # 测试报告编号
    REPORT_NO: Final = 'FlaskDBResultStorage__report_no'

    # 测试集合编号
    COLLECTION_NO: Final = 'FlaskDBResultStorage__collection_no'

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

    @property
    def last_sample_ok(self) -> bool:
        return ContextService.get_context().variables.get('Coroutine__last_sample_ok')

    def __init__(self):
        TestElement.__init__(self)
        self.flask_instance = getattr(importlib.import_module('app'), '__app__')
        self.table_model = importlib.import_module('app.script.model')
        self.TTestCollectionResult = self.table_model.TTestCollectionResult  # noqa
        self.TTestGroupResult = self.table_model.TTestGroupResult  # noqa
        self.TTestSamplerResult = self.table_model.TTestSamplerResult  # noqa
        self.success: bool = True
        self.collection_start_time = 0
        self.collection_end_time = 0

    def collection_started(self) -> None:
        """@override"""
        # 记录 Collection 开始时间
        self.collection_start_time = timestamp_now()
        # 插入 Collection 数据至数据库
        self.insert_test_collection_result()

    def collection_ended(self) -> None:
        """@override"""
        # 记录 Collection 结束时间
        self.collection_end_time = timestamp_now()
        # 更新 Collection 数据
        self.update_test_collection_result()

    def group_started(self) -> None:
        """@override"""
        # 记录 Group 开始时间
        self.group.start_time = timestamp_now()
        self.group.success = True
        # 插入 Group 数据至数据库
        self.insert_test_group_result()

    def group_finished(self) -> None:
        """@override"""
        # 记录 Group 结束时间
        self.group.end_time = timestamp_now()
        # 更新 Group 数据
        self.update_test_group_result()

    def sample_occurred(self, result: SampleResult) -> None:
        """@override"""
        # 最后一个 Sample 失败时，同步更新 Group/Collection 的结果也为失败
        if not self.last_sample_ok:
            self.group.success = False
            self.success = False
        # 递归插入 Sampler 和 SubSampler 数据至数据库
        self.sampler_occurred_with_subresults(result)

    def sampler_occurred_with_subresults(self, result: SampleResult):
        # 插入 Sampler 数据至数据库
        self.insert_test_sampler_result(result)
        if result.sub_results:
            for sub in result.sub_results:
                self.sampler_occurred_with_subresults(sub)

    def sample_started(self, sample) -> None:
        """@override"""
        pass

    def sample_ended(self, result: SampleResult) -> None:
        """@override"""
        pass

    def insert_test_collection_result(self):
        logger.debug('insert collection result')
        with self.flask_instance.app_context():
            self.TTestCollectionResult.insert(
                REPORT_NO=self.report_no,
                COLLECTION_NO=self.collection_no,
                COLLECTION_ID=self.collection_id,
                COLLECTION_NAME=self.collection.name,
                COLLECTION_REMARK=self.collection.remark,
                START_TIME=timestmp_to_utc8_datetime(self.collection_start_time),
                SUCCESS=True,
                CREATED_BY='PyMeter',
                UPDATED_BY='PyMeter',
                record=False
            )

    def insert_test_group_result(self):
        logger.debug('insert group result')
        with self.flask_instance.app_context():
            self.TTestGroupResult.insert(
                REPORT_NO=self.report_no,
                COLLECTION_ID=self.collection_id,
                GROUP_ID=self.group_id,
                GROUP_NAME=self.group.name,
                GROUP_REMARK=self.group.remark,
                START_TIME=timestmp_to_utc8_datetime(self.group.start_time),
                SUCCESS=True,
                CREATED_BY='PyMeter',
                UPDATED_BY='PyMeter',
                record=False
            )

    def insert_test_sampler_result(self, result: SampleResult):
        logger.debug('insert sampler result')
        failed_assertion_data = None
        if result.assertions:
            assertions = [assertion for assertion in result.assertions if assertion.failure or assertion.error]
            if len(assertions) > 0:
                failed_assertion_data = assertions[0].message

        with self.flask_instance.app_context():
            self.TTestSamplerResult.insert(
                REPORT_NO=self.report_no,
                COLLECTION_ID=self.collection_id,
                GROUP_ID=self.group_id,
                PARENT_ID=id(result.parent) if result.parent else None,
                SAMPLER_ID=id(result),
                SAMPLER_NAME=result.sample_name,
                SAMPLER_REMARK=result.sample_remark,
                START_TIME=timestmp_to_utc8_datetime(result.start_time),
                END_TIME=timestmp_to_utc8_datetime(result.end_time),
                ELAPSED_TIME=result.elapsed_time,
                SUCCESS=result.success,
                RETRYING=result.retrying,
                REQUEST_URL=result.request_url,
                REQUEST_HEADERS=(
                    to_json(result.request_headers)
                    if not isinstance(result.request_headers, str)
                    else result.request_headers
                ),
                REQUEST_DATA=(
                    to_json(result.request_data)
                    if not isinstance(result.request_data, str)
                    else result.request_data
                ),
                RESPONSE_CODE=str(result.response_code),
                RESPONSE_HEADERS=(
                    to_json(result.response_headers)
                    if not isinstance(result.response_headers, str)
                    else result.response_headers
                ),
                RESPONSE_DATA=(
                    to_json(result.response_data)
                    if not isinstance(result.response_data, str)
                    else result.response_data
                ),
                FAILED_ASSERTION=failed_assertion_data,
                CREATED_BY='PyMeter',
                UPDATED_BY='PyMeter',
                record=False
            )

    def update_test_collection_result(self):
        logger.debug('update collection result')
        elapsed_time = int(self.collection_end_time * 1000) - int(self.collection_start_time * 1000)
        with self.flask_instance.app_context():
            self.TTestCollectionResult.filter_by(COLLECTION_ID=str(self.collection_id)).update({
                'END_TIME': timestmp_to_utc8_datetime(self.collection_end_time),
                'ELAPSED_TIME': elapsed_time,
                'SUCCESS': self.success,
                'UPDATED_BY': 'PyMeter'
            })

    def update_test_group_result(self):
        logger.debug('update group result')
        elapsed_time = int(self.group.end_time * 1000) - int(self.group.start_time * 1000)
        with self.flask_instance.app_context():
            self.TTestGroupResult.filter_by(GROUP_ID=str(self.group_id)).update({
                'END_TIME': timestmp_to_utc8_datetime(self.group.end_time),
                'ELAPSED_TIME': elapsed_time,
                'SUCCESS': self.group.success,
                'UPDATED_BY': 'PyMeter'
            })
