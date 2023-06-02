#!/usr/bin python3
# @File    : collection.py
# @Time    : 2020/2/24 15:35
# @Author  : Kelvin.Ye
from typing import Final

from pymeter.elements.element import TestElement


class Collection(TestElement):

    # 运行策略
    RUNNING_STRATEGY = 'Collection__running_strategy'

    @property
    def running_strategy(self):
        default = {
            # 筛选
            # logic: [AND, OR]
            # field: [TYPE, LEVEL]
            # operator: [EQUAL, NOT_EQUAL, IN, NOT_IN]
            # value:
            #   TYPE: [PRE, POST, ASSERT]
            #   LEVEL: [WORKSPACE, COLLECTION, WORKER, CONTROLLER, SAMPLER]
            # {
            #     "filter": {
            #         "logic": "",
            #         "rules": [
            #             {"field": "", "operator": "", "value": ""},    # condition
            #             {"logic": "", "rules": []}                       # group
            #         ]
            #     }
            # }
            'filter': [],
            # 倒序执行: [1:前置，2:后置，3:断言]
            'reverse': []
        }
        strategy = self.get_property(self.RUNNING_STRATEGY).get_obj()
        return strategy or default


class TestCollection(Collection):

    # 运行策略
    RUNNING_STRATEGY: Final = 'TestCollection__running_strategy'

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
