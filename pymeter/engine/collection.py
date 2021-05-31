#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : collection.py
# @Time    : 2020/2/24 15:35
# @Author  : Kelvin.Ye
from pymeter.elements.element import TestElement
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class TestCollection(TestElement):
    # 是否顺序执行任务组
    SERIALIZE_GROUPS = 'TestCollection__serialize_groups'

    # 延迟启动任务组，单位ms
    DELAY = 'TestCollection__delay'

    @property
    def serialized(self):
        return self.get_property_as_bool(self.SERIALIZE_GROUPS)

    @property
    def delay(self):
        return self.get_property_as_int(self.DELAY)
