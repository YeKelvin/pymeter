#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : exception.py
# @Time    : 2019/3/15 10:48
# @Author  : Kelvin.Ye


class InvalidVariableException(Exception):
    ...


class InvalidPropertyException(Exception):
    ...


class EngineException(Exception):
    ...


class ScriptParseException(Exception):
    ...


class NextIsNullException(Exception):
    ...


class StopCoroutineGroupException(Exception):
    ...


class StopTestException(Exception):
    ...


class StopTestNowException(Exception):
    ...


class ProjectBaseDirectoryNotFoundException(Exception):
    ...


class UnsupportedOperationException(Exception):
    ...
