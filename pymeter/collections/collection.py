#!/usr/bin python3
# @File    : collection.py
# @Time    : 2020/2/24 15:35
# @Author  : Kelvin.Ye
from pymeter.elements.element import TestElement


class Collection(TestElement):

    # 运行策略
    RUNNING_STRATEGY = None

    @property
    def running_strategy(self):
        # 默认策略
        default = {
            # 筛选
            # logic: [AND, OR]
            # operator: [EQUAL, NOT_EQUAL, IN, NOT_IN]
            # field: [TYPE, LEVEL]
            # value:
            #   TYPE: [PREV, POST, ASSERT]
            #   LEVEL: [WORKSPACE, COLLECTION, WORKER, CONTROLLER, SAMPLER]
            # e.g.:
            # {
            #     "filter": {
            #         "logic": "",
            #         "rules": [
            #             {"field": "", "operator": "", "value": ""},  # condition
            #             {"logic": "", "rules": []}                   # group
            #         ]
            #     }
            # }
            'filter': [],
            # 倒序执行: [PREV, POST, ASSERT]
            'reverse': []
        }
        return self.get_property(self.RUNNING_STRATEGY).get_obj() or default
