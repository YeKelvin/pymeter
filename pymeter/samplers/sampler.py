#!/usr/bin python3
# @File    : sampler.py
# @Time    : 2020/1/24 23:47
# @Author  : Kelvin.Ye
from pymeter.elements.element import TestElement
from pymeter.engines.variables import Variables


class Sampler(TestElement):

    # 运行策略
    RUNNING_STRATEGY = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__args__ = Variables()

    @property
    def running_strategy(self):
        return self.get_property(self.RUNNING_STRATEGY).get_obj()

    def sample(self):
        raise NotImplementedError
