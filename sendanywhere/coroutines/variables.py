#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : variables
# @Time    : 2019/3/14 11:08
# @Author  : Kelvin.Ye
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class SenderVariables:
    def __init__(self):
        self.variables = {}

    def put(self, key: str, value: str) -> None:
        self.variables[key] = value

    def get(self, key: str) -> str:
        return self.variables.get(key)

    def remove(self, key: str) -> None:
        del self.variables[key]

    def clear(self) -> None:
        self.variables.clear()

    def keys(self):
        return self.variables.keys()
