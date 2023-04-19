#!/usr/bin python3
# @File    : base64_util.py
# @Time    : 2022/10/13 09:20
# @Author  : Kelvin.Ye
import base64


def encode(data):
    return base64.b64encode(data.encode('utf8')).decode('utf8')


def decode(ciphertext):
    return base64.b64decode(ciphertext.encode('utf8'))
