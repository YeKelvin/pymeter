#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : gevent_test.py
# @Time    : 2020/2/23 14:12
# @Author  : Kelvin.Ye
from datetime import datetime

import gevent


def test():
    start_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f'startTime={start_time}')
    gevent.sleep(1)
    end_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f'endTime={end_time}')


if __name__ == '__main__':
    t1 = gevent.spawn(test)
    t2 = gevent.spawn(test)
    gevent.joinall([t1, t2])
