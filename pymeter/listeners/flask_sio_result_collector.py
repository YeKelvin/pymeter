#!/usr/bin python3
# @File    : flask_sio_result_collector.py
# @Time    : 2021/10/15 16:44
# @Author  : Kelvin.Ye
import importlib
from typing import Final

import arrow
from dateutil import tz

from pymeter.elements.element import TestElement
from pymeter.engine.interface import NoThreadClone
from pymeter.engine.interface import SampleListener
from pymeter.engine.interface import TestCollectionListener
from pymeter.engine.interface import TestIterationListener
from pymeter.engine.interface import TestWorkerListener
from pymeter.utils.time_util import strftime_now
from pymeter.utils.time_util import timestamp_now
from pymeter.workers.context import ContextService


class FlaskSIOResultCollector(
    TestElement, TestCollectionListener, TestWorkerListener, SampleListener, TestIterationListener, NoThreadClone
):

    # 消息接收方的 sid
    SID: Final = 'FlaskSIOResultCollector__sid'

    RESULT_ID: Final = 'FlaskSIOResultCollector__result_id'

    RESULT_NAME: Final = 'FlaskSIOResultCollector__result_name'

    @property
    def sid(self):
        return self.get_property_as_str(self.SID)

    @property
    def result_id(self):
        return self.get_property_as_str(self.RESULT_ID)

    @property
    def result_name(self):
        return self.get_property_as_str(self.RESULT_NAME)

    @property
    def worker(self):
        return ContextService.get_context().worker

    @property
    def worker_id(self):
        return str(id(self.worker))

    @property
    def last_sample_ok(self) -> bool:
        return ContextService.get_context().variables.get('Coroutine__last_sample_ok')

    def __init__(self):
        TestElement.__init__(self)

        self.collection_start_time = 0
        self.collection_end_time = 0

        self.flask_sio = None
        self.flask_sio_instance_module = 'app.extension'
        self.flask_sio_instance_name = 'socketio'

        self.namespace = '/'
        self.result_summary_event = 'pymeter_result_summary'
        self.result_worker_event = 'pymeter_worker_result'
        self.result_sampler_event = 'pymeter_sampler_result'

    def init_flask_sio(self):
        module = importlib.import_module(self.flask_sio_instance_module)
        self.flask_sio = getattr(module, self.flask_sio_instance_name)

    def emit(self, name, data):
        self.flask_sio.emit(name, data, namespace=self.namespace, to=self.sid)

    def get_collection_elapsed_time(self):
        return int(self.collection_end_time * 1000) - int(self.collection_start_time * 1000)

    def collection_started(self) -> None:
        """@override"""
        self.collection_start_time = timestamp_now()
        self.init_flask_sio()
        self.emit(self.result_summary_event, {
            'resultId': self.result_id,
            'result': {
                'id': self.result_id,
                'name': self.result_name,
                'startTime': to_strftime(self.collection_start_time),
                'endTime': 0,
                'elapsedTime': 0,
                'loading': False,
                'running': True,
                'details': []
            }
        })

    def collection_ended(self) -> None:
        """@override"""
        self.collection_end_time = timestamp_now()
        self.emit(self.result_summary_event, {
            'resultId': self.result_id,
            'result': {
                'endTime': to_strftime(self.collection_end_time),
                'elapsedTime': self.get_collection_elapsed_time(),
                'running': False
            }
        })

    def worker_started(self) -> None:
        """@override"""
        setattr(self.worker, 'start_time', timestamp_now())
        setattr(self.worker, 'success', True)
        self.emit(self.result_worker_event, {
            'resultId': self.result_id,
            'workerId': self.worker_id,
            'worker': {
                'id': self.worker_id,
                'name': self.worker.name,
                'startTime': strftime_now(),
                'endTime': 0,
                'elapsedTime': 0,
                'running': True,
                'success': True,
                'children': []
            }
        })

    def worker_finished(self) -> None:
        """@override"""
        setattr(self.worker, 'end_time', timestamp_now())
        worker_success = getattr(self.worker, 'success')
        worker_start_time = getattr(self.worker, 'start_time')
        worker_end_time = getattr(self.worker, 'end_time')
        worker_elapsed_time = int(worker_end_time * 1000) - int(worker_start_time * 1000)
        self.emit(self.result_worker_event, {
            'resultId': self.result_id,
            'workerId': self.worker_id,
            'worker': {
                'endTime': strftime_now(),
                'elapsedTime': worker_elapsed_time,
                'running': False,
                'success': worker_success
            }
        })

    def sample_occurred(self, result) -> None:
        """@override"""
        # 最后一个 Sample 失败时，同步更新 Worker 的结果也为失败
        if not self.last_sample_ok:
            setattr(self.worker, 'success', False)
        self.emit(self.result_sampler_event, {
            'resultId': self.result_id,
            'workerId': self.worker_id,
            'sampler': sample_result_to_dict(result)
        })

    def sample_started(self, sample) -> None:
        """@override"""
        ...

    def sample_ended(self, result) -> None:
        """@override"""
        ...

    def test_iteration_start(self, controller, iter) -> None:
        ...


def sample_result_to_dict(result):
    return {
        'id': str(id(result)),
        'name': result.sample_name,
        'remark': result.sample_remark,
        'url': result.request_url,
        'request': result.request_data,
        'requestHeaders': result.request_headers,
        'response': result.response_data,
        'responseHeaders': result.response_headers,
        'responseCode': result.response_code,
        'responseMessage': result.response_message,
        'requestSize': result.request_size,
        'responseSize': result.response_size,
        'success': result.success,
        'retrying': result.retrying,
        'startTime': to_strftime(result.start_time),
        'endTime': to_strftime(result.end_time),
        'elapsedTime': result.elapsed_time,
        'failedAssertion': next(
            (
                {'message': assertion.message}
                for assertion in result.assertions
                if assertion.failure or assertion.error
            ),
            None,
        ),
        'children': [sample_result_to_dict(sub) for sub in result.sub_results]
    }


def to_strftime(timestamp):
    return arrow.Arrow.fromtimestamp(timestamp, tzinfo=tz.gettz('Asia/Shanghai')).format('HH:mm:ss.SSS')
