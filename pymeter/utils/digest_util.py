#!/usr/bin python3
# @File    : digest_util.py
# @Time    : 2023-06-14 15:44:41
# @Author  : Kelvin.Ye
import base64
import hashlib
import hmac
from hashlib import sha256


def md5(data, charset='utf-8'):
    return hashlib.md5(data.encode(encoding=charset)).hexdigest()


def hmac_sha256(data, key=None, charset='utf-8') -> bytes:
    if key:
        key = key.encode(charset)
    return hmac.new(key, data.encode(charset), digestmod=sha256).digest()


def hmac_sha256_hex(data, key=None, charset='utf-8') -> str:
    if key:
        key = key.encode(charset)
    return hmac.new(key, data.encode(charset), digestmod=sha256).hexdigest().upper()


def hmac_sha256_base64(data, key=None, charset='utf-8') -> str:
    if key:
        key = key.encode(charset)
    return base64.b64encode(
        hmac.new(key, data.encode(charset), digestmod=sha256).digest()
    ).decode(charset)
