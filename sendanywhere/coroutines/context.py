#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : context
# @Time    : 2019/3/15 9:39
# @Author  : Kelvin.Ye
import time

from gevent.local import local

from sendanywhere.coroutines.variables import Variables
from sendanywhere.engine.globalization import SenderUtils
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class CoroutineContext:
    def __init__(self):
        self.variables = Variables()
        self.coroutine = None
        self.coroutine_group = None
        self.coroutine_number = None
        self.coroutine_name = None
        # self.sampler_context = None  # todo 有啥用
        # self.sampling_started = False  # todo 有啥用
        self.current_sampler = None
        self.previous_sampler = None
        self.previous_result = None
        self.engine = None

    def clear(self):
        self.variables = None
        self.coroutine = None
        self.coroutine_group = None
        self.coroutine_number = None
        self.current_sampler = None
        self.previous_sampler = None
        self.previous_result = None

    def set_current_sampler(self, sampler):
        self.previous_sampler = self.current_sampler
        self.current_sampler = sampler

    def set_previous_result(self, result):
        self.previous_result = result


class EngineContext:
    def __init__(self):
        self.test_start = 0
        self.number_of_active_threads = 0
        self.number_of_threads_started = 0
        self.number_of_threads_finished = 0
        self.total_threads = 0


class ContextService:
    # 协程本地变量
    coroutine_local = local()
    engines: {str, EngineContext} = {}

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
    def replace_context(cls, context) -> None:
        if hasattr(cls.coroutine_local, 'coroutine_context'):
            cls.coroutine_local.coroutine_context = context

    @classmethod
    def start_test(cls, engine_id=None):
        engine_ctx = cls.__get_engine_context(engine_id)
        if engine_ctx.test_start == 0:
            engine_ctx.numberOfActiveThreads = 0
            engine_ctx.test_start = int(time.time() * 1000)
            SenderUtils.set_property('TESTSTART.MS', engine_ctx.test_start)

    @classmethod
    def end_test(cls, engine_id=None):
        engine_ctx = cls.__get_engine_context(engine_id)
        engine_ctx.test_start = 0

    @classmethod
    def incr_number_of_coroutines(cls, engine_id=None):
        """增加活动线程的数量
        """
        engine_ctx = cls.__get_engine_context(engine_id)
        engine_ctx.number_of_active_threads += 1
        engine_ctx.number_of_threads_started += 1

    @classmethod
    def decr_number_of_coroutines(cls, engine_id=None):
        """减少活动线程的数量
        """
        engine_ctx = cls.__get_engine_context(engine_id)
        engine_ctx.number_of_active_threads -= 1
        engine_ctx.number_of_threads_finished += 1

    @classmethod
    def add_total_coroutines(cls, group_number, engine_id=None):
        engine_ctx = cls.__get_engine_context(engine_id)
        engine_ctx.total_threads += group_number

    @classmethod
    def clear_total_coroutines(cls, engine_id=None):
        engine_ctx = cls.__get_engine_context(engine_id)
        engine_ctx.total_threads = 0
        engine_ctx.number_of_threads_started = 0
        engine_ctx.number_of_threads_finished = 0

    @classmethod
    def __get_engine_context(cls, engine_id) -> EngineContext:
        if not engine_id:
            engine_id = cls.get_context().engine.id
        return cls.engines.get(engine_id, EngineContext())
