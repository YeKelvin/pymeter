#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log_util.py
# @Time    : 2019/3/15 10:56
# @Author  : Kelvin.Ye
import datetime as dt
import logging
import threading

from pymeter import config as CONFIG


class ExternalSocketIOHandler(logging.Handler):

    LOCAL = threading.local()

    def __init__(self, level=logging.INFO):
        logging.Handler.__init__(self)
        self.terminator = '\n'
        self.setLevel(level)

    def emit(self, record):
        if not hasattr(self.LOCAL, 'sio') and not hasattr(self.LOCAL, 'sid'):
            return
        msg = self.format(record) + self.terminator
        self.LOCAL.sio.emit('pymeter_log', msg, namespace='/', to=self.LOCAL.sid)


class ExternalSocketIOFormatter(logging.Formatter):

    converter = dt.datetime.fromtimestamp

    default_time_format = '%H:%M:%S'
    default_msec_format = '%s.%03d'

    def formatTime(self, record, datefmt=None):
        ct = dt.datetime.fromtimestamp(record.created)
        t = ct.strftime(self.default_time_format)
        s = self.default_msec_format % (t, record.msecs)
        return s


# 日志格式
LOG_FORMAT = '[%(asctime)s][%(levelname)s][%(threadName)s][%(name)s.%(funcName)s %(lineno)d] %(message)s'
FORMATTER = logging.Formatter(LOG_FORMAT)
# 日志级别
LEVEL = CONFIG.LOG_LEVEL
# 日志文件名称
LOG_FILE_NAME = CONFIG.LOG_NAME


# 输出到控制台
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(FORMATTER)

# 写入日志文件
FILE_HANDLER = logging.FileHandler(LOG_FILE_NAME, encoding='utf-8')
FILE_HANDLER.setFormatter(FORMATTER)

# 通过 SocketIo 传递日志
EXTERNAL_SOCKET_IO_HANDLER = ExternalSocketIOHandler()
EXTERNAL_SOCKET_IO_HANDLER.setFormatter(
    ExternalSocketIOFormatter(fmt='[%(asctime)s][%(levelname)s][%(name)s:%(lineno)d] %(message)s')
)


def get_logger(name) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(LEVEL)
    logger.addHandler(CONSOLE_HANDLER)
    # logger.addHandler(FILE_HANDLER)
    logger.addHandler(EXTERNAL_SOCKET_IO_HANDLER)
    return logger
