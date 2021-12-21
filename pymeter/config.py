#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : config.py
# @Time    : 2021-11-03 23:19:13
# @Author  : Kelvin.Ye
import configparser
import os


# 项目路径
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# 源代码目录路径
SRC_PATH = os.path.join(PROJECT_PATH, 'pymeter')
# 配置文件路径
if 'APP_CONFIG_FILE' not in os.environ:
    APP_CONFIG_FILE = os.path.join(PROJECT_PATH, 'config.ini')
    os.environ['APP_CONFIG_FILE'] = APP_CONFIG_FILE
else:
    APP_CONFIG_FILE = os.environ.get('APP_CONFIG_FILE')


# 配置对象
__config__ = configparser.ConfigParser()
__config__.read(APP_CONFIG_FILE)


# 配置项
# 日志相关配置
LOG_LEVEL = __config__.get('log', 'level')
