#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : collection.py
# @Time    : 2020/2/24 15:35
# @Author  : Kelvin.Ye
from sendanywhere.testelement.test_element import TestElement
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class TestCollection(TestElement):
    # 是否顺序执行线程组
    SERIALIZE_COROUTINEGROUPS = 'TestCollection.serialized'

    @property
    def serialized(self):
        return self.get_property_as_bool(self.SERIALIZE_COROUTINEGROUPS)
