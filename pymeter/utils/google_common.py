#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : google_common.py
# @Time    : 2021-08-17 19:03:54
# @Author  : Kelvin.Ye
import base64
import hashlib
import hmac
import struct
import time


class GoogleAuthenticate:
    @staticmethod
    def get_code(secret_key):
        key = base64.b32decode(secret_key, True)
        intervals_no = int(time.time()) // 30
        msg = struct.pack(">Q", intervals_no)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = ord(chr(h[19])) & 15
        h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
        code = '%06d' % h
        return code


if __name__ == '__main__':
    key = 'SCALISVBXQQ2JBQN'
    google_code = GoogleAuthenticate.get_code(key)
    print(google_code)
