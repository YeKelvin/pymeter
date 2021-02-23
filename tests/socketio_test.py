#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : socketio_test.py
# @Time    : 2021/1/10 17:24
# @Author  : Kelvin.Ye
import socketio


sio = socketio.Client(logger=True, engineio_logger=True)


@sio.on('connect')
def on_connect():
    print(f'i am connect, sid={sio.sid}')


@sio.on('disconnect')
def on_disconnect():
    print(f'disconnect, sid={sio.sid}')


@sio.on('message')
def on_message(data):
    print(f'I received a message, data={data}')


if __name__ == '__main__':
    sio.connect('http://127.0.0.1:5000', namespaces=['/'])
    sio.sleep(2.0)

    sio.emit('test', {'data': 'emit: i am sendanywhere'})
    sio.send('send: i am sendanywhere')

    print('done')
    sio.sleep(2.0)
    sio.disconnect()
