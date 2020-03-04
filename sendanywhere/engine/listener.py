#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : listener
# @Time    : 2020/2/26 11:25
# @Author  : Kelvin.Ye


class TestStateListener:
    def test_started(self) -> None:
        raise NotImplementedError

    def test_ended(self) -> None:
        raise NotImplementedError


class CoroutineGroupListener:
    def group_started(self) -> None:
        raise NotImplementedError

    def group_finished(self) -> None:
        raise NotImplementedError


class SampleListener:
    def sample_started(self, sample) -> None:
        raise NotImplementedError

    def sample_ended(self, sample_result) -> None:
        raise NotImplementedError


class TestIterationListener:
    def test_iteration_start(self, controller) -> None:
        raise NotImplementedError


class LoopIterationListener:
    def iteration_start(self, source, iter_count) -> None:
        """在循环迭代即将开始时调用
        """
        raise NotImplementedError


class IteratingController:
    def start_next_loop(self) -> None:
        raise NotImplementedError

    def break_loop(self) -> None:
        raise NotImplementedError
