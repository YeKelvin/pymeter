#!/usr/bin python3
# @File    : sampler.py
# @Time    : 2020/1/24 23:47
# @Author  : Kelvin.Ye
from pymeter.elements.element import TestElement


class Sampler(TestElement):

    # 运行策略
    RUNNING_STRATEGY = 'Sampler__running_strategy'

    @property
    def running_strategy(self):
        return self.get_property(self.RUNNING_STRATEGY).get_obj()

    def sample(self):
        raise NotImplementedError
