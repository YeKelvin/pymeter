#!/usr/bin python3
# @File    : worker.py
# @Time    : 2023-05-22 15:02:22
# @Author  : Kelvin.Ye
from pymeter.controls.controller import Controller


class Worker(Controller):

    # 运行策略
    RUNNING_STRATEGY = 'Worker__running_strategy'

    @property
    def running_strategy(self):
        return self.get_property(self.RUNNING_STRATEGY).get_obj()
