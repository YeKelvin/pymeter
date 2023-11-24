#!/usr/bin python3
# @File    : flask_db_result_storage.py
# @Time    : 2021-09-09 21:17:33
# @Author  : Kelvin.Ye
import importlib
from typing import Final

from pymeter.elements.element import TestElement
from pymeter.engines.interface import NoThreadClone
from pymeter.engines.interface import SampleListener
from pymeter.engines.interface import TestCollectionListener
from pymeter.engines.interface import TestWorkerListener
from pymeter.samplers.sample_result import SampleResult
from pymeter.utils.json_util import to_json
from pymeter.utils.time_util import timestamp_now
from pymeter.utils.time_util import timestmp_to_utc8_datetime
from pymeter.workers.context import ContextService


class FlaskDBResultStorage(TestElement, TestCollectionListener, TestWorkerListener, SampleListener, NoThreadClone):

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
    def worker(self):
        return ContextService.get_context().worker

    @property
    def worker_id(self):
        return id(self.worker)

    @property
    def last_sample_ok(self) -> bool:
        return ContextService.get_context().variables.get('Coroutine__last_sample_ok')

    def __init__(self):
        TestElement.__init__(self)
        self.success: bool = True
        self.collection_start_time = 0
        self.collection_end_time = 0

        self.db_instance = getattr(importlib.import_module('app.extension'), 'db')
        self.flask_instance = getattr(importlib.import_module('app'), '__app__')

        table_model = importlib.import_module('app.modules.script.model')
        self.TTestCollectionResult = getattr(table_model, 'TTestCollectionResult')
        self.TTestWorkerResult = getattr(table_model, 'TTestWorkerResult')
        self.TTestSamplerResult = getattr(table_model, 'TTestSamplerResult')

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

    def worker_started(self) -> None:
        """@override"""
        # 记录 Worker 开始时间
        setattr(self.worker, 'start_time', timestamp_now())
        setattr(self.worker, 'success', True)
        # 插入 Worker 数据至数据库
        self.insert_test_worker_result()

    def worker_finished(self) -> None:
        """@override"""
        # 记录 Worker 结束时间
        setattr(self.worker, 'end_time', timestamp_now())
        # 更新 Worker 数据
        self.update_test_worker_result()

    def sample_occurred(self, result: SampleResult) -> None:
        """@override"""
        # 最后一个 Sample 失败时，同步更新 Worker/Collection 的结果也为失败
        if not self.last_sample_ok:
            setattr(self.worker, 'success', False)
            self.success = False
        # 递归插入 Sampler 和 SubSampler 数据至数据库
        self.sampler_occurred_with_subresults(result)

    def sampler_occurred_with_subresults(self, result: SampleResult):
        # 插入 Sampler 数据至数据库
        self.insert_test_sampler_result(result)
        if result.subresults:
            for sub in result.subresults:
                self.sampler_occurred_with_subresults(sub)

    def sample_started(self, sample) -> None:
        """@override"""
        pass

    def sample_ended(self, result: SampleResult) -> None:
        """@override"""
        pass

    def insert_test_collection_result(self):
        with self.flask_instance.app_context():
            self.TTestCollectionResult.norecord_insert(
                REPORT_NO=self.report_no,
                COLLECTION_NO=self.collection_no,
                COLLECTION_ID=self.collection_id,
                COLLECTION_NAME=self.collection.name,
                COLLECTION_DESC=self.collection.desc,
                START_TIME=timestmp_to_utc8_datetime(self.collection_start_time),
                SUCCESS=True,
                CREATED_BY='PyMeter',
                UPDATED_BY='PyMeter'
            )
            self.db_instance.session.commit()

    def insert_test_worker_result(self):
        with self.flask_instance.app_context():
            self.TTestWorkerResult.norecord_insert(
                REPORT_NO=self.report_no,
                COLLECTION_ID=self.collection_id,
                WORKER_ID=self.worker_id,
                WORKER_NAME=self.worker.name,
                WORKER_DESC=self.worker.desc,
                START_TIME=timestmp_to_utc8_datetime(self.worker.start_time),
                SUCCESS=True,
                CREATED_BY='PyMeter',
                UPDATED_BY='PyMeter'
            )
            self.db_instance.session.commit()

    def insert_test_sampler_result(self, result: SampleResult):
        failed_assertion_data = None
        if result.assertions:
            if assertions := [
                assertion
                for assertion in result.assertions
                if assertion.failure or assertion.error
            ]:
                failed_assertion_data = assertions[0].message

        with self.flask_instance.app_context():
            self.TTestSamplerResult.norecord_insert(
                REPORT_NO=self.report_no,
                COLLECTION_ID=self.collection_id,
                WORKER_ID=self.worker_id,
                PARENT_ID=id(result.parent) if result.parent else None,
                SAMPLER_ID=id(result),
                SAMPLER_NAME=result.sample_name,
                SAMPLER_DESC=result.sample_desc,
                START_TIME=timestmp_to_utc8_datetime(result.start_time),
                END_TIME=timestmp_to_utc8_datetime(result.end_time),
                ELAPSED_TIME=result.elapsed_time,
                SUCCESS=result.success,
                RETRYING=result.retrying,
                REQUEST_URL=result.request_url,
                REQUEST_HEADERS=(
                    result.request_headers
                    if isinstance(result.request_headers, str)
                    else to_json(result.request_headers)
                ),
                REQUEST_DATA=(
                    result.request_data
                    if isinstance(result.request_data, str)
                    else to_json(result.request_data)
                ),
                REQUEST_DECODED=result.request_decoded,
                RESPONSE_CODE=str(result.response_code),
                RESPONSE_HEADERS=(
                    result.response_headers
                    if isinstance(result.response_headers, str)
                    else to_json(result.response_headers)
                ),
                RESPONSE_DATA=(
                    result.response_data
                    if isinstance(result.response_data, str)
                    else to_json(result.response_data)
                ),
                RESPONSE_DECODED=result.response_decoded,
                FAILED_ASSERTION=failed_assertion_data,
                CREATED_BY='PyMeter',
                UPDATED_BY='PyMeter'
            )
            self.db_instance.session.commit()

    def update_test_collection_result(self):
        elapsed_time = int(self.collection_end_time * 1000) - int(self.collection_start_time * 1000)
        with self.flask_instance.app_context():
            (
                self.TTestCollectionResult
                .filter_by(COLLECTION_ID=str(self.collection_id))
                .update({
                    'END_TIME': timestmp_to_utc8_datetime(self.collection_end_time),
                    'ELAPSED_TIME': elapsed_time,
                    'SUCCESS': self.success,
                    'UPDATED_BY': 'PyMeter'
                })
            )
            self.db_instance.session.commit()

    def update_test_worker_result(self):
        worker_success = getattr(self.worker, 'success')
        worker_start_time = getattr(self.worker, 'start_time')
        worker_end_time = getattr(self.worker, 'end_time')
        elapsed_time = int(worker_end_time * 1000) - int(worker_start_time * 1000)
        with self.flask_instance.app_context():
            (
                self.TTestWorkerResult
                .filter_by(WORKER_ID=str(self.worker_id))
                .update({
                    'END_TIME': timestmp_to_utc8_datetime(worker_end_time),
                    'ELAPSED_TIME': elapsed_time,
                    'SUCCESS': worker_success,
                    'UPDATED_BY': 'PyMeter'
                })
            )
            self.db_instance.session.commit()
