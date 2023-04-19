#!/usr/bin python3
# @File    : flask_sio_result_collector.py
# @Time    : 2021/10/15 16:44
# @Author  : Kelvin.Ye
import importlib
from typing import Final

from pymeter.elements.element import TestElement
from pymeter.engine.interface import NoCoroutineClone
from pymeter.engine.interface import SampleListener
from pymeter.engine.interface import TestCollectionListener
from pymeter.engine.interface import TestGroupListener
from pymeter.engine.interface import TestIterationListener
from pymeter.groups.context import ContextService
from pymeter.utils import time_util
from pymeter.utils.time_util import timestamp_now
from pymeter.utils.time_util import timestamp_to_strftime


class FlaskSIOResultCollector(
    TestElement, TestCollectionListener, TestGroupListener, SampleListener, TestIterationListener, NoCoroutineClone
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
    def group(self):
        return ContextService.get_context().group

    @property
    def group_id(self):
        return str(id(self.group))

    @property
    def last_sample_ok(self) -> bool:
        return ContextService.get_context().variables.get('Coroutine__last_sample_ok')

    def __init__(self):
        TestElement.__init__(self)

        self.flask_sio = None
        self.flask_sio_instance_module = 'app.extension'
        self.flask_sio_instance_name = 'socketio'

        self.namespace = '/'
        self.result_summary_event = 'pymeter_result_summary'
        self.result_group_event = 'pymeter_group_result'
        self.result_sampler_event = 'pymeter_sampler_result'

        self.collection_start_time = 0
        self.collection_end_time = 0

    def init_flask_sio(self):
        module = importlib.import_module(self.flask_sio_instance_module)
        self.flask_sio = getattr(module, self.flask_sio_instance_name)

    def emit(self, name, data):
        self.flask_sio.emit(name, data, namespace=self.namespace, to=self.sid)

    def collection_started(self) -> None:
        """@override"""
        self.collection_start_time = timestamp_now()
        self.init_flask_sio()
        self.emit(self.result_summary_event, {
            'resultId': self.result_id,
            'result': {
                'id': self.result_id,
                'name': self.result_name,
                'startTime': timestamp_to_strftime(self.collection_start_time),
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
                'endTime': timestamp_to_strftime(self.collection_end_time),
                'elapsedTime': int(self.collection_end_time * 1000) - int(self.collection_start_time * 1000),
                'running': False
            }
        })

    def group_started(self) -> None:
        """@override"""
        self.group.start_time = timestamp_now()
        self.group.success = True
        self.emit(self.result_group_event, {
            'resultId': self.result_id,
            'groupId': self.group_id,
            'group': {
                'id': self.group_id,
                'name': self.group.name,
                'startTime': time_util.strftime_now(),
                'endTime': 0,
                'elapsedTime': 0,
                'running': True,
                'success': True,
                'children': []
            }
        })

    def group_finished(self) -> None:
        """@override"""
        self.group.end_time = timestamp_now()
        self.emit(self.result_group_event, {
            'resultId': self.result_id,
            'groupId': self.group_id,
            'group': {
                'endTime': time_util.strftime_now(),
                'elapsedTime': int(self.group.end_time * 1000) - int(self.group.start_time * 1000),
                'running': False,
                'success': self.group.success
            }
        })

    def sample_occurred(self, result) -> None:
        """@override"""
        # 最后一个 Sample 失败时，同步更新 Group 的结果也为失败
        if not self.last_sample_ok:
            self.group.success = False
        self.emit(self.result_sampler_event, {
            'resultId': self.result_id,
            'groupId': self.group_id,
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
        'startTime': time_util.timestamp_to_strftime(result.start_time),
        'endTime': time_util.timestamp_to_strftime(result.end_time),
        'elapsedTime': result.elapsed_time,
        'failedAssertion': failed_assertion(result.assertions),
        'children': [sample_result_to_dict(sub) for sub in result.sub_results]
    }


def failed_assertion(assertions):
    for assertion in assertions:
        if assertion.failure or assertion.error:
            return {
                'message': assertion.message
            }
    return None
