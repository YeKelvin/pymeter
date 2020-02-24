#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : search_by_class
# @Time    : 2020/2/24 14:55
# @Author  : Kelvin.Ye
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class SearchByClass:
    def __init__(self, clazz: type):
        self.search_class = clazz
