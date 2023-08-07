#!/usr/bin python3
# @File    : log_util.py
# @Time    : 2019/3/15 10:56
# @Author  : Kelvin.Ye
import logging


class SocketIOHandler(logging.Handler):

    def __init__(self, sio, sid, level=logging.INFO):
        logging.Handler.__init__(self)
        self.terminator = '\n'
        self.setLevel(level)
        self.sio = sio
        self.sid = sid

    def emit(self, record):
        if record.extra.get('sid') != self.sid:
            return
        self.sio.emit('pymeter:log', self.format(record) + self.terminator, namespace='/', to=self.sid)
