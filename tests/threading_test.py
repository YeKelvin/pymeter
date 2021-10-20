#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : threading_test.py.py
# @Time    : 2021/10/20 17:35
# @Author  : Kelvin.Ye
import threading
import gevent

from threading import local
# from gevent.local import local

thread_local = local()


def f1(parent):
    global thread_local
    print(f'parent={parent}, f1, gevent, aa={thread_local.aa}')


def f2(parent):
    global thread_local
    print(f'parent={parent}, f2, gevent, aa={thread_local.aa}')


def fmain(aa):
    thread_local.aa = aa
    print(f'fmain, thread, aa={thread_local.aa}')
    t1 = gevent.spawn(f1, aa)
    t2 = gevent.spawn(f2, aa)
    gevent.joinall([t1, t2])


if __name__ == '__main__':
    target1 = threading.Thread(target=fmain, args=['111'])
    target2 = threading.Thread(target=fmain, args=['222'])

    target1.start()
    target2.start()

    target1.join()
    target2.join()
