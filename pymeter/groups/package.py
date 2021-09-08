#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sample_package
# @Time    : 2020/2/27 15:41
# @Author  : Kelvin.Ye
from typing import List

from pymeter.assertions.assertion import Assertion
from pymeter.controls.controller import Controller
from pymeter.elements.element import ConfigElement
from pymeter.engine.interface import SampleListener
from pymeter.processors.post import PostProcessor
from pymeter.processors.pre import PreProcessor
from pymeter.timers.timer import Timer
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class SamplePackage:

    def __init__(
        self,
        configs: List[ConfigElement] = [],
        listeners: List[SampleListener] = [],
        timers: List[Timer] = [],
        assertions: List[Assertion] = [],
        post_processors: List[PostProcessor] = [],
        pre_processors: List[PreProcessor] = [],
        controllers: List[Controller] = []
    ):
        self.configs = configs
        self.listeners = listeners
        self.timers = timers
        self.assertions = assertions
        self.post_processors = post_processors
        self.pre_processors = pre_processors
        self.controllers = controllers

        self.sampler = None

    def set_running_version(self, running) -> None:
        log.debug(f'set running version in package, running:[ {running} ]')
        for el in self.configs:
            el.running_version = running
        for el in self.pre_processors:
            el.running_version = running
        for el in self.listeners:
            el.running_version = running
        for el in self.post_processors:
            el.running_version = running
        for el in self.assertions:
            el.running_version = running
        for el in self.timers:
            el.running_version = running
        for el in self.controllers:
            el.running_version = running
        self.sampler.running_version = running

    def recover_running_version(self) -> None:
        log.debug('recover running version in package')
        for el in self.configs:
            el.recover_running_version()
        for el in self.pre_processors:
            el.recover_running_version()
        for el in self.listeners:
            el.recover_running_version()
        for el in self.post_processors:
            el.recover_running_version()
        for el in self.assertions:
            el.recover_running_version()
        for el in self.timers:
            el.recover_running_version()
        for el in self.controllers:
            el.recover_running_version()
        self.sampler.recover_running_version()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str({
            'sampler': self.sampler,
            'configs': [config for config in self.configs],
            'controllers': [controller for controller in self.controllers],
            'listeners': [listener for listener in self.listeners],
            'timers': [time for time in self.timers],
            'assertions': [assertion for assertion in self.assertions],
            'pres': [processor for processor in self.pre_processors],
            'posts': [processor for processor in self.post_processors],
        })
