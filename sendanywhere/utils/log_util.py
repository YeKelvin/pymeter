#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_util.py
# @Time    : 2019/3/15 10:56
# @Author  : Kelvin.Ye
import logging

from sendanywhere.utils import project


# 日志格式
LOG_FORMAT = '[%(asctime)s][%(levelname)s][%(threadName)s][%(name)s.%(funcName)s %(lineno)d] %(message)s'

# 日志级别
LEVEL = project.config.get('log', 'level', default='INFO')

# 日志文件名称
LOG_FILE_NAME = project.config.get('log', 'name', default='sendanywhere')

# 日志格式
FORMATTER = logging.Formatter(LOG_FORMAT)

# 输出到控制台
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(FORMATTER)

# 写入日志文件
# FILE_HANDLER = logging.FileHandler(LOG_FILE_NAME, encoding='utf-8')
# FILE_HANDLER.setFormatter(FORMATTER)


def get_logger(name) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(LEVEL)
    logger.addHandler(CONSOLE_HANDLER)
    # logger.addHandler(FILE_HANDLER)
    return logger
