#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sample_package
# @Time    : 2020/2/27 15:41
# @Author  : Kelvin.Ye
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class SamplePackage:
    def __init__(self):
        self.configs = []
        self.controllers = []
        self.preProcessors = []
        self.listeners = []
        self.postProcessors = []
        self.assertions = []
