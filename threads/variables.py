#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : variables.py
# @Time    : 2019/3/14 11:08
# @Author  : KelvinYe
from typing import KeysView, _KT


class PyatVariables:
    def __init__(self):
        self.variables = dict()

    def put(self, key: str, value: str) -> None:
        self.variables[key] = value

    def get(self, key: str) -> str:
        return self.variables.get(key)

    def remove(self, key: str) -> None:
        del self.variables[key]

    def clear(self) -> None:
        self.variables.clear()

    def keys(self) -> KeysView[_KT]:
        return self.variables.keys()
