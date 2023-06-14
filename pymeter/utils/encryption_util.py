#!/usr/bin python3
# @File    : encryption_util.py
# @Time    : 2023-06-14 15:44:41
# @Author  : Kelvin.Ye
import hashlib
import hmac
from hashlib import sha256


def md5(data, charset='utf-8'):
    return hashlib.md5(data.encode(encoding=charset)).hexdigest()


def hmac_sha256(data, key, charset='utf-8'):
    return hmac.new(key.encode(charset), data.encode(charset), digestmod=sha256).hexdigest().upper()
