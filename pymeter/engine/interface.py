#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : interface.py
# @Time    : 2020/2/26 11:25
# @Author  : Kelvin.Ye


class TestCollectionListener:

    def collection_started(self) -> None:
        """测试执行在开始时调用"""
        raise NotImplementedError

    def collection_ended(self) -> None:
        """测试执行在结束时调用"""
        raise NotImplementedError


class TestGroupListener:

    def group_started(self) -> None:
        """TestGroup在开始时调用"""
        raise NotImplementedError

    def group_finished(self) -> None:
        """TestGroup在结束时调用"""
        raise NotImplementedError


class SampleListener:

    def sample_started(self, sample) -> None:
        """Sampler在开始时调用"""
        raise NotImplementedError

    def sample_ended(self, sample_result) -> None:
        """Sampler在结束时调用"""
        raise NotImplementedError


class TestIterationListener:

    def test_iteration_start(self, controller) -> None:
        """TestGroup在迭代开始时调用"""
        raise NotImplementedError


class LoopIterationListener:

    def iteration_start(self, source, iter_count) -> None:
        """控制器在循环迭代即将开始时调用"""
        raise NotImplementedError
