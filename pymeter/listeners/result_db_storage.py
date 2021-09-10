#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : flask_result_storage.py
# @Time    : 2021-09-09 21:17:33
# @Author  : Kelvin.Ye
from datetime import datetime
from typing import Final

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.engine import Engine

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


class ResultDBStorage(
    TestElement, TestCollectionListener, TestGroupListener, SampleListener, TestIterationListener, NoCoroutineClone
):

    # 数据库连接串
    DATABASE_URL: Final = 'ResultDBStorage__database_url'

    # 测试计划编号
    PLAN_NO: Final = 'ResultDBStorage__plan_no'

    # 测试报告编号
    REPORT_NO: Final = 'ResultDBStorage__report_no'

    # 测试集合编号
    COLLECTION_NO: Final = 'ResultDBStorage__collection_no'

    @property
    def database_url(self):
        return self.get_property_as_str(self.DATABASE_URL)

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

        self.engine: Engine = None
        self.connection: Connection = None
        self.success: bool = True

    def init_db(self):
        log.debug(f'连接数据库，连接地址:[ {self.database_url} ]')
        self.engine = create_engine(self.database_url)
        self.connection = self.engine.connect()

    def collection_started(self) -> None:
        """@override"""
        # 初始化数据库
        self.init_db()
        # 记录 Collection 开始时间
        self.collection_start_time = time_util.timestamp_now()
        # 插入 Collection 数据至数据库
        self.insert_test_collection_result()

    def collection_ended(self) -> None:
        """@override"""
        log.debug('关闭数据库连接')
        self.connection.close()
        # 记录 Collection 结束时间
        self.collection_end_time = time_util.timestamp_now()
        # 更新 Collection 数据
        self.update_test_collection_result()

    def group_started(self) -> None:
        """@override"""
        start_time = time_util.timestamp_now()
        # 记录 Group 开始时间
        self.group.start_time = start_time
        # 插入 Group 数据至数据库
        self.insert_test_group_result(start_time)

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

    def insert_test_collection_result(self, collection_name, collection_remark):
        expression = f"""
        insert into TEST_COLLECTION_RESULT (DEL_STATE, REPORT_NO, COLLECTION_NO, COLLECTION_ID,
                                            COLLECTION_NAME, COLLECTION_REMARK, START_TIME, SUCCESS,
                                            CREATED_BY, CREATED_TIME, UPDATED_BY, UPDATED_TIME)
        values  (0,
                {self.report_no},
                {self.collection_no},
                {self.collection_id},
                '{self.collection.name}',
                '{self.collection.remark}',
                {self.collection_start_time},
                {True},
                'PyMeter',
                {datetime.utcnow()},
                'PyMeter',
                {datetime.utcnow()});
        """
        log.debug('insert collection result')
        result = self.connection.execute(expression)
        log.debug(result.rowcount)

    def insert_test_group_result(self, start_time):
        expression = f"""
        insert into TEST_GROUP_RESULT (DEL_STATE, REPORT_NO, COLLECTION_ID, GROUP_ID,
                                        GROUP_NAME, GROUP_REMARK, START_TIME, SUCCESS,
                                        CREATED_BY, CREATED_TIME, UPDATED_BY, UPDATED_TIME)
        values  (0,
                {self.report_no},
                {self.collection_id},
                {self.group_id},
                '{self.group.name}',
                '{self.group.remark}',
                {start_time},
                {True},
                'PyMeter',
                {datetime.utcnow()},
                'PyMeter',
                {datetime.utcnow()});
        """
        log.debug('insert group result')
        result = self.connection.execute(expression)
        log.debug(result.rowcount)

    def insert_test_sampler_result(self, result: SampleResult):
        err_assertion_data = None
        if result.assertions:
            assertions = [assertion for assertion in result.assertions if assertion.failure or assertion.error]
            if len(assertions) > 0:
                err_assertion_data = assertions[0].message

        expression = f"""
        insert into TEST_SAMPLER_RESULT (DEL_STATE, REPORT_NO, GROUP_ID, PARENT_ID, SAMPLER_ID,
                                        SAMPLER_NAME, SAMPLER_REMARK, START_TIME, END_TIME, ELAPSED_TIME, SUCCESS,
                                        REQUEST_URL, REQUEST_DATA, REQUEST_HEADERS,
                                        RESPONSE_DATA, RESPONSE_HEADERS,
                                        ERROR_ASSERTION,
                                        CREATED_BY, CREATED_TIME, UPDATED_BY, UPDATED_TIME)
        values  (0,
                {self.report_no},
                {self.group_id},
                {id(result.parent) if result.parent else None},
                {id(result)},
                '{result.sample_name}',
                '{result.sample_remark}',
                {result.start_time},
                {result.end_time},
                {result.elapsed_time},
                {result.success},
                '{result.request_url}',
                '{result.request_data}',
                '{result.request_headers}',
                '{result.response_data}',
                '{result.response_headers}',
                '{err_assertion_data}'
                'PyMeter',
                {datetime.utcnow()},
                'PyMeter',
                {datetime.utcnow()});
        """
        log.debug('insert sampler result')
        result = self.connection.execute(expression)
        log.debug(result.rowcount)

    def update_test_collection_result(self):
        elapsed_time = int(self.collection_end_time * 1000) - int(self.collection_start_time * 1000)
        expression = f"""
        update TEST_COLLECTION_RESULT
        set END_TIME={self.collection_end_time}
            ELAPSED_TIME={elapsed_time}
            SUCCESS={self.success}
        where COLLECTION_ID='{self.collection_id}'
        """
        log.debug('update collection result')
        result = self.connection.execute(expression)
        log.debug(result.rowcount)

    def update_test_group_result(self):
        success = getattr(self.group, 'success', True)
        elapsed_time = int(self.group.end_time * 1000) - int(self.group.start_time * 1000)
        expression = f"""
        update TEST_GROUP_RESULT
        set END_TIME={self.group.end_time}
            ELAPSED_TIME={elapsed_time}
            SUCCESS={success}
        where GROUP_ID='{self.group_id}'
        """
        log.debug('update group result')
        result = self.connection.execute(expression)
        log.debug(result.rowcount)
