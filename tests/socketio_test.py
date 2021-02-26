#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : socketio_test.py
# @Time    : 2021/1/10 17:24
# @Author  : Kelvin.Ye
import socketio


sio = socketio.Client(logger=True, engineio_logger=True)


@sio.on('connect')
def handle_connect():
    print(f'socket sid:[ {sio.sid} ] event:[ connect ]')


@sio.on('disconnect')
def handle_disconnect():
    print(f'socket sid:[ {sio.sid} ] event:[ disconnect ]')


@sio.on('execution_result')
def handle_execution_result(data):
    print(f'socket sid:[ {sio.sid} ] event:[ execution_result ] received data:[ {data} ]')


if __name__ == '__main__':
    sio.connect('http://127.0.0.1:5000')
    sio.sleep(2.0)

    sio.emit('execution_result', {'to': '-1IB6-NAOtyKQdeiAAAB', 'data': 'i am sendanywhere'})

    sio.sleep(5.0)
    # sio.disconnect()
    # print('done')
