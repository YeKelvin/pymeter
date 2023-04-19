#!/usr/bin python3
# @File    : collection.py
# @Time    : 2020/2/24 15:35
# @Author  : Kelvin.Ye
from pymeter.elements.element import TestElement


class TestCollection(TestElement):

    # 是否顺序执行 TestGroup
    SERIALIZE_GROUPS = 'TestCollection__serialize_groups'

    # 延迟启动 TestGroup ，单位ms
    DELAY = 'TestCollection__delay'

    @property
    def serialized(self):
        return self.get_property_as_bool(self.SERIALIZE_GROUPS)

    @property
    def delay(self):
        return self.get_property_as_int(self.DELAY)
