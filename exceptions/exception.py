#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : exception.py
# @Time    : 2019/3/15 10:48
# @Author  : KelvinYe


class InvalidVariableException(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(self, msg)
