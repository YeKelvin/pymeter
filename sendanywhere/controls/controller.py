#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : controller.py
# @Time    : 2020/2/28 16:01
# @Author  : Kelvin.Ye
from sendanywhere.samplers.sampler import Sampler


class Controller:
    def __init__(self):
        # 控制器是否已完成所有取样器的交付，当返回true时，协程完成
        self.is_done = False

    def next(self) -> Sampler:
        """返回下一个取样器，末尾返回None
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


class IteratingController:
    """迭代控制器
    """

    def start_next_loop(self) -> None:
        """开始下一个迭代
        """
        raise NotImplementedError

    def break_loop(self) -> None:
        """中断循环
        """
        raise NotImplementedError
