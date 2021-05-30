#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : globalization.py
# @Time    : 2020/2/20 21:34
# @Author  : Kelvin.Ye
from typing import Dict

from tasker.groups.context import ContextService


class GlobalProperties(dict):
    def put(self, key: str, value: any) -> None:
        self[key] = value


class GlobalUtils:
    __all_global_properties: Dict[str, GlobalProperties] = {}

    @classmethod
    def set_property(cls, key: str, value: any, engine_id=None) -> None:
        if not engine_id:
            engine_id = cls.engine_id()
        if engine_id not in cls.__all_global_properties:
            cls.__all_global_properties[engine_id] = GlobalProperties()
        cls.__all_global_properties.get(engine_id).put(key, value)

    @classmethod
    def get_property(cls, key: str, defalut=None, engine_id=None):
        if not engine_id:
            engine_id = cls.engine_id()
        if engine_id not in cls.__all_global_properties:
            cls.__all_global_properties[engine_id] = GlobalProperties()
        return cls.__all_global_properties.get(engine_id).get(key, defalut)

    @classmethod
    def get_properties(cls, engine_id=None):
        if not engine_id:
            engine_id = cls.engine_id()
        if engine_id not in cls.__all_global_properties:
            cls.__all_global_properties[engine_id] = GlobalProperties()
        return cls.__all_global_properties.get(engine_id)

    @staticmethod
    def engine_id():
        return ContextService.get_context().engine.id
