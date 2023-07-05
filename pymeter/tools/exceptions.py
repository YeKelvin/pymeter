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


class ScriptParseError(Exception):
    ...


class NodeParseError(Exception):
    ...


class NextIsNullException(Exception):
    ...


class StopTestWorkerException(Exception):
    ...


class StopTestException(Exception):
    ...


class StopTestNowException(Exception):
    ...


class UnsupportedOperationError(Exception):
    ...


class HttpHeaderDuplicateException(Exception):
    ...


class HttpCookieDuplicateException(Exception):
    ...


class FunctionError(Exception):
    ...
