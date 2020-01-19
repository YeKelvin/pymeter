#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_util.py
# @Time    : 2019/3/15 10:56
# @Author  : KelvinYe

import logging

from src.core.pers.kelvin.pyautotest.utils import config

# LogLevel: NOTSET，DEBUG，INFO，WARNING，CRITICAL, ERROR
level = config.get('log', 'level')


def getlogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # fh = logging.FileHandler(config.get('log').get('name'))  # 用于写入日志文件
    ch = logging.StreamHandler()  # 用于输出到控制台

    # 定义handler的输出格式
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s.%(funcName)s] %(message)s')
    # fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 给logger添加handler
    # logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
