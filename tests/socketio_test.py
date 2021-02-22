#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : socketio_test.py
# @Time    : 2021/1/10 17:24
# @Author  : Kelvin.Ye
import socketio


sio = socketio.Client(logger=True, engineio_logger=True)


@sio.on('connect')
def on_connect():
    print('i am connect')


@sio.on('event')
def on_event(data):
    print('i am event')


if __name__ == '__main__':
    sio.connect('http://127.0.0.1:5000', namespaces=['/'])
    # print('start wait')
    # sio.wait()
    # print('wait finish')
    sio.sleep(2.0)
    sio.emit('test', {'data': 'i am sendanywhere'}, namespace='/')
    # sio.send('i am sendanywhere')
    print(f'sid={sio.sid}')
    print('done')
    sio.sleep(2.0)
    sio.disconnect()
