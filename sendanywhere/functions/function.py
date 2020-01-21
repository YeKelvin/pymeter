#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : function
# @Time    : 2020/1/19 17:05
# @Author  : Kelvin.Ye
from sendanywhere.utils.class_finder import ClassFinder
from sendanywhere.utils.log_util import get_logger

log = get_logger(__name__)


class Function:
    REF_KEY = '__referenceKey'

    def execute(self):
        raise NotImplementedError

    def set_parameters(self, parameters: []):
        raise NotImplementedError

    def check_parameter_count(self, min=None, max=None, count=None):
        raise NotImplementedError

    def check_min_parameter_count(self):
        raise NotImplementedError


def __init_functions__():
    functions = {}
    classes = ClassFinder.find_subclasses(Function)
    for clazz in classes:
        reference_key = clazz.REF_KEY
        if reference_key:
            functions[reference_key] = clazz
    return functions


FUNCTIONS_STORE = __init_functions__()
