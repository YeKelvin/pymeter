#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : listener
# @Time    : 2020/2/26 11:25
# @Author  : Kelvin.Ye


class TestStateListener:
    def test_started(self):
        raise NotImplementedError

    def test_ended(self):
        raise NotImplementedError


class CoroutineGroupListener:
    def group_started(self):
        raise NotImplementedError

    def group_finished(self):
        raise NotImplementedError


class SampleListener:
    def sample_started(self, sample_event):
        raise NotImplementedError

    def sample_stopped(self, sample_event):
        raise NotImplementedError
