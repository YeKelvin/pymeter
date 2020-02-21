#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : globalization.py
# @Time    : 2020/2/20 21:34
# @Author  : Kelvin.Ye


class SenderUtils:
    __global_properties = {}

    @classmethod
    def set_property(cls, key: str, value: any) -> None:
        cls.__global_properties[key] = value

    @classmethod
    def get_property(cls, key: str):
        return cls.__global_properties[key]
