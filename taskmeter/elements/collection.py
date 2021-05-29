#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : collection.py
# @Time    : 2020/2/24 15:35
# @Author  : Kelvin.Ye
from taskmeter.elements.element import TestElement
from taskmeter.utils.log_util import get_logger


log = get_logger(__name__)


class TaskCollection(TestElement):
    # 是否顺序执行协程组
    SERIALIZE_GROUPS = 'TaskCollection__serialize_groups'

    # 延迟启动协程组，单位ms
    DELAY = 'TaskCollection__delay'

    @property
    def serialized(self):
        return self.get_property_as_bool(self.SERIALIZE_GROUPS)

    @property
    def delay(self):
        return self.get_property_as_int(self.DELAY)
