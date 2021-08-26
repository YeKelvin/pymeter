#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : interface.py
# @Time    : 2020/2/26 11:25
# @Author  : Kelvin.Ye


class TestCollectionListener:

    def collection_started(self) -> None:
        """在 TestCollection 开始前调用"""
        raise NotImplementedError

    def collection_ended(self) -> None:
        """在 TestCollection 结束后调用"""
        raise NotImplementedError


class TestGroupListener:

    def group_started(self) -> None:
        """在 TestGroup 开始前调用"""
        raise NotImplementedError

    def group_finished(self) -> None:
        """在 TestGroup 结束后调用"""
        raise NotImplementedError


class SampleListener:

    def sample_occurred(self, result) -> None:
        """在 SamplerPackage 完成后调用"""
        raise NotImplementedError

    def sample_started(self, sample) -> None:
        """在 Sampler 开始前调用"""
        raise NotImplementedError

    def sample_ended(self, result) -> None:
        """在 Sampler 结束后调用"""
        raise NotImplementedError


class TestIterationListener:

    def test_iteration_start(self, controller) -> None:
        """在 TestGroup 迭代开始前调用"""
        raise NotImplementedError


class LoopIterationListener:

    def iteration_start(self, source, iter_count) -> None:
        """控制器在循环迭代即将开始前调用"""
        raise NotImplementedError


class NoConfigMerge:
    ...


class NoCoroutineClone:
    ...
