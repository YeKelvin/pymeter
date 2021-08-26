#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sample_package
# @Time    : 2020/2/27 15:41
# @Author  : Kelvin.Ye
from pymeter.assertions.assertion import Assertion
from pymeter.elements.element import ConfigElement
from pymeter.engine.interface import SampleListener
from pymeter.processors.post import PostProcessor
from pymeter.processors.pre import PreProcessor
from pymeter.timers.timer import Timer
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class SamplePackage:

    def __init__(self, sampler=None):
        self.sampler = sampler
        self.configs = []
        self.pre_processors = []
        self.listeners = []
        self.post_processors = []
        self.assertions = []
        self.timers = []

    def save_sampler(self, nodes: list):
        for node in nodes:
            if isinstance(node, ConfigElement):
                self.configs.append(node)
            elif isinstance(node, PreProcessor):
                self.pre_processors.append(node)
            elif isinstance(node, SampleListener):
                self.listeners.append(node)
            elif isinstance(node, PostProcessor):
                self.post_processors.append(node)
            elif isinstance(node, Assertion):
                self.assertions.append(node)
            elif isinstance(node, Timer):
                self.timers.append(node)

    def save_transaction_controller(self, nodes: list):
        for node in nodes:
            if isinstance(node, SampleListener):
                self.listeners.append(node)
            elif isinstance(node, Assertion):
                self.assertions.append(node)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str({
            'sampler': self.sampler,
            'configs': '[' + ''.join([str(config) + ',' for config in self.configs])[:-1] + ']',
            'pre-processors': '[' + ''.join([str(processor) + ',' for processor in self.pre_processors])[:-1] + ']',
            'listeners': '[' + ''.join([str(listener) + ',' for listener in self.listeners])[:-1] + ']',
            'post-processors': '[' + ''.join([str(processor) + ',' for processor in self.post_processors])[:-1] + ']',
            'assertions': '[' + ''.join([str(assertion) + ',' for assertion in self.assertions])[:-1] + ']',
            'timers': '[' + ''.join([str(time) + ',' for time in self.timers])[:-1] + ']',
        })
