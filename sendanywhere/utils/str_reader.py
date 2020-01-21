#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : str_reader
# @Time    : 2020/1/20 9:36
# @Author  : Kelvin.Ye


class StringReader:
    def __init__(self, string: str):
        self.raw = string
        self.__iter: iter = string.__iter__()

    @property
    def next(self) -> str or None:
        try:
            return self.__iter.__next__()
        except StopIteration:
            return None

    def reset(self) -> None:
        self.__iter = self.raw.__iter__()
