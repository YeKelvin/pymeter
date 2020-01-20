#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : function
# @Time    : 2020/1/19 17:05
# @Author  : Kelvin.Ye
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class Function:
    def execute(self):
        pass

    def set_parameters(self):
        pass

    def get_reference_key(self):
        pass

    def check_parameter_count(self, min=None, max=None, count=None):
        pass

    def check_min_parameter_count(self):
        pass
