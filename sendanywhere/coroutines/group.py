#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : group.py
# @Time    : 2020/2/13 12:58
# @Author  : Kelvin.Ye
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class CoroutineGroup(TestElement):
    # Sampler失败时的处理动作
    # 枚举：continue | start_next_loop | stop_coroutine | stop_test
    ON_SAMPLE_ERROR = 'CoroutineGroup.on_sample_error'

    # 是否无限循环
    CONTINUE_FOREVER = 'CoroutineGroup.continue_forever'

    # 循环次数
    LOOPS = 'CoroutineGroup.loops'

    # 线程数
    NUMBER_COROUTINES = 'CoroutineGroup.number_coroutines'

    # 启用线程的间隔时间，单位 s
    START_INTERVAL = 'CoroutineGroup.start_interval'

    def __init__(self, name: str = None, comments: str = None, propertys: dict = None):
        super().__init__(name, comments, propertys)
        self.running = False
