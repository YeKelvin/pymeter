#!/usr/bin python3
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

    def test_iteration_start(self, controller, iter: int) -> None:
        """在 TestGroup 迭代开始前调用"""
        raise NotImplementedError


class LoopIterationListener:

    def iteration_start(self, source, iter) -> None:
        """控制器在迭代即将开始前调用"""
        raise NotImplementedError


class TransactionListener:

    def transaction_started(self) -> None:
        """在 TransactionController 开始前调用"""
        raise NotImplementedError

    def transaction_ended(self) -> None:
        """在 TransactionController 结束后调用"""
        raise NotImplementedError


class TestCompilerHelper:

    def add_test_element_once(self, child) -> bool:
        raise NotImplementedError


class NoConfigMerge:
    ...


class NoCoroutineClone:
    ...


class TransactionConfig:
    ...
