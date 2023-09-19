#!/usr/bin python3
# @File    : gevent_test.py
# @Time    : 2020/2/23 14:12
# @Author  : Kelvin.Ye
from datetime import UTC
from datetime import datetime

import gevent
from gevent import Greenlet
from gevent.local import local


coroutine_local = local()


class Test(Greenlet):
    def _run(self):
        print('I am test')
        start_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f'startTime={start_time}')
        coroutine_local.aa = 'aa'
        print(f'coroutine_local.aa={coroutine_local.aa}')
        gevent.sleep(1)
        end_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f'endTime={end_time}')


if __name__ == '__main__':
    test = Test()
    g = Greenlet(test.run)
    g.run()
    print(g.minimal_ident)
    print(gevent.getcurrent())
