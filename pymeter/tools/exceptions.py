#!/usr/bin python3
# @File    : exception.py
# @Time    : 2019/3/15 10:48
# @Author  : Kelvin.Ye


class InvalidScriptException(Exception):
    ...


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


class StopTestGroupException(Exception):
    ...


class StopTestException(Exception):
    ...


class StopTestNowException(Exception):
    ...


class ProjectBaseDirectoryNotFoundException(Exception):
    ...


class UnsupportedOperationException(Exception):
    ...


class HttpHeaderDuplicateException(Exception):
    ...


class HttpCookieDuplicateException(Exception):
    ...
