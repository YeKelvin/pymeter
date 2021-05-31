#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : project.py
# @Time    : 2021/5/9 22:35
# @Author  : Kelvin.Ye
import os
from functools import lru_cache

from pymeter.utils.ini_reader import IniConfig
from pymeter.utils.path_util import find_invoker_project_root


# 项目名称
name = None


@lru_cache
def root_path():
    """项目根目录路径"""
    return find_invoker_project_root(name)


@lru_cache
def config_path():
    """配置文件路径"""
    return os.path.join(root_path(), 'config.ini')


config = IniConfig(config_path())


@lru_cache
def resources_path():
    """项目资源目录路径"""
    resources = os.path.normpath(config.get('path', 'resources'))
    return os.path.join(root_path(), resources)
