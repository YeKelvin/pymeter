#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : variables
# @Time    : 2020/3/4 15:12
# @Author  : Kelvin.Ye


class Variables(dict):

    def __init__(self):
        super().__init__()
        self.iteration = 0

    def inc_iteration(self):
        self.iteration += 1

    def put(self, key: str, value: any) -> None:
        self[key] = value
