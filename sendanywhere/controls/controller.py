#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : controller.py
# @Time    : 2020/2/28 16:01
# @Author  : Kelvin.Ye
from sendanywhere.samplers.sampler import Sampler


class Controller:
    def next(self) -> Sampler:
        """返回下一个取样器，末尾返回None
        """
        raise NotImplementedError

    def is_done(self):
        """
        控制器是否已完成所有测试的交付
        当返回true时，协程完成
        """
        raise NotImplementedError

    def initialize(self):
        """在迭代开始时调用以初始化控制器
        """
        raise NotImplementedError

    def trigger_end_of_loop(self):
        """在控制器上触发循环结束条件
        """
        raise NotImplementedError
