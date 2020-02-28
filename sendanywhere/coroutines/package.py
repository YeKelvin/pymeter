#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sample_package
# @Time    : 2020/2/27 15:41
# @Author  : Kelvin.Ye
from sendanywhere.assertions.assertion import Assertion
from sendanywhere.configs.config import ConfigElement
from sendanywhere.controls.controller import Controller
from sendanywhere.engine.listener import SampleListener
from sendanywhere.processors.post import PostProcessor
from sendanywhere.processors.pre import PreProcessor
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class SamplePackage:
    def __init__(self):
        self.configs = []
        self.controllers = []
        self.pre_processors = []
        self.listeners = []
        self.post_processors = []
        self.assertions = []

    def add(self, node_list: list):
        for node in node_list:
            if isinstance(node, ConfigElement):
                self.configs.append(node)
            if isinstance(node, Controller):
                self.controllers.append(node)
            if isinstance(node, PreProcessor):
                self.pre_processors.append(node)
            if isinstance(node, SampleListener):
                self.listeners.append(node)
            if isinstance(node, PostProcessor):
                self.post_processors.append(node)
            if isinstance(node, Assertion):
                self.assertions.append(node)
