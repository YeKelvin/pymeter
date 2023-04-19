#!/usr/bin python3
# @File    : context
# @Time    : 2019/3/15 9:39
# @Author  : Kelvin.Ye
from threading import local as ThreadLocal

from gevent.local import local as CoroutineLocal

from pymeter.groups.variables import Variables
from pymeter.utils import time_util


class CoroutineContext:

    @property
    def properties(self):
        return getattr(self.engine, 'properties', {})

    @property
    def extra(self):
        return getattr(self.engine, 'extra', {})

    def __init__(self):
        self.variables = Variables()
        self.engine = None
        self.group = None
        self.coroutine = None
        self.coroutine_number = None
        self.coroutine_name = None
        self.current_sampler = None
        self.previous_sampler = None
        self.previous_result = None

    def clear(self):
        self.variables = None
        self.group = None
        self.coroutine = None
        self.coroutine_number = None
        self.current_sampler = None
        self.previous_sampler = None
        self.previous_result = None

    def set_current_sampler(self, sampler):
        self.previous_sampler = self.current_sampler
        self.current_sampler = sampler

    def set_previous_result(self, result):
        self.previous_result = result


class ContextService:

    # 线程本地变量
    thread_local = ThreadLocal()

    # 协程本地变量
    coroutine_local = CoroutineLocal()

    @classmethod
    def get_context(cls) -> CoroutineContext:
        if not hasattr(cls.coroutine_local, 'coroutine_context'):
            setattr(cls.coroutine_local, 'coroutine_context', CoroutineContext())
        return cls.coroutine_local.coroutine_context

    @classmethod
    def remove_context(cls) -> None:
        if hasattr(cls.coroutine_local, 'coroutine_context'):
            del cls.coroutine_local.coroutine_context

    @classmethod
    def replace_context(cls, ctx) -> None:
        setattr(cls.coroutine_local, 'coroutine_context', ctx)

    @classmethod
    def start_test(cls):
        engine_ctx = cls.get_context().engine.context
        if engine_ctx.test_start == 0:
            engine_ctx.number_of_threads_actived = 0
            engine_ctx.test_start = time_util.timestamp_now()
            cls.get_context().properties.put('TESTSTART.MS', engine_ctx.test_start)

    @classmethod
    def end_test(cls):
        engine_ctx = cls.get_context().engine.context
        engine_ctx.test_start = 0

    @classmethod
    def incr_number_of_threads(cls):
        """增加活动线程的数量"""
        engine_ctx = cls.get_context().engine.context
        engine_ctx.number_of_threads_actived += 1
        engine_ctx.number_of_threads_started += 1

    @classmethod
    def decr_number_of_threads(cls):
        """减少活动线程的数量"""
        engine_ctx = cls.get_context().engine.context
        engine_ctx.number_of_threads_actived -= 1
        engine_ctx.number_of_threads_finished += 1

    @classmethod
    def add_total_threads(cls, group_number):
        engine_ctx = cls.get_context().engine.context
        engine_ctx.total_threads += group_number

    @classmethod
    def clear_total_threads(cls):
        engine_ctx = cls.get_context().engine.context
        engine_ctx.total_threads = 0
        engine_ctx.number_of_threads_started = 0
        engine_ctx.number_of_threads_finished = 0
