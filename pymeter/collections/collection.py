#!/usr/bin python3
# @File    : collection.py
# @Time    : 2020/2/24 15:35
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.elements.element import TestElement


class Collection(TestElement):

    # 元素配置
    CONFIG = 'Collection__config'

    @property
    def config(self):
        default = {
            'components': {
                # 类型: [1前置，2后置，3断言]，级别: [0空间，1集合，2工作线程，3控制器]
                'include': {"type": [], "level": []},
                'exclude': {"type": [], "level": []},
                # 倒序执行: [1前置，2后置，3断言]
                'reverse': []
            }
        }
        _config_ = self.get_property(self.CONFIG).get_obj()
        return _config_ or default


class TestCollection(Collection):

    # 元素配置
    CONFIG: Final = 'TestCollection__config'

    # 是否顺序执行 TestGroup
    SERIALIZE_GROUPS: Final = 'TestCollection__serialize_groups'

    # 延迟启动 TestGroup ，单位ms
    DELAY: Final = 'TestCollection__delay'

    @property
    def serialized(self):
        return self.get_property_as_bool(self.SERIALIZE_GROUPS)

    @property
    def delay(self):
        return self.get_property_as_int(self.DELAY)
