#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : listener
# @Time    : 2020/2/26 11:25
# @Author  : Kelvin.Ye


class TestStateListener:
    def test_started(self) -> None:
        """测试执行在开始时调用
        """
        raise NotImplementedError

    def test_ended(self) -> None:
        """测试执行在结束时调用
        """
        raise NotImplementedError


class TaskGroupListener:
    def group_started(self) -> None:
        """协程组在开始时调用
        """
        raise NotImplementedError

    def group_finished(self) -> None:
        """协程组在结束时调用
        """
        raise NotImplementedError


class SampleListener:
    def sample_started(self, sample) -> None:
        """取样器在开始时调用
        """
        raise NotImplementedError

    def sample_ended(self, sample_result) -> None:
        """取样器在结束时调用
        """
        raise NotImplementedError


class TestIterationListener:
    def test_iteration_start(self, controller) -> None:
        """协程组在迭代开始时调用
        """
        raise NotImplementedError


class LoopIterationListener:
    def iteration_start(self, source, iter_count) -> None:
        """控制器在循环迭代即将开始时调用
        """
        raise NotImplementedError


class NoCoroutineClone:
    pass
