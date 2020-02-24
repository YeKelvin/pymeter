#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : gevent_test.py
# @Time    : 2020/2/23 14:12
# @Author  : Kelvin.Ye
from datetime import datetime

import gevent
from gevent.local import local

coroutine_local = local()


def test():
    print('I am test')
    # start_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    # print(f'startTime={start_time}')
    coroutine_local.aa = 'aa'
    coroutine_local.bb = 'bb'
    print(f'coroutine_local={coroutine_local}')
    print(f'coroutine_local.aa={coroutine_local.aa}')
    print(f'coroutine_local.bb={coroutine_local.bb}')
    # gevent.sleep(1)
    # end_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    # print(f'endTime={end_time}')


def test_local():
    print('I am test_local')
    print(f'coroutine_local={coroutine_local}')
    # print(f'coroutine_local.aa={coroutine_local.aa}')


if __name__ == '__main__':
    t1 = gevent.spawn(test)
    t2 = gevent.spawn(test)
    t3 = gevent.spawn(test_local())
    gevent.joinall([t1, t2, t3])
