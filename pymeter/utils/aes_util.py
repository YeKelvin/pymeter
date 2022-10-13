#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : aes_util.py
# @Time    : 2022/10/12 18:15
# @Author  : Kelvin.Ye
import base64
import binascii

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad


"""
AES加密有AES-128、AES-192、AES-256三种，分别对应三种密钥长度
128bits（16字节）、192bits（24字节）、256bits（32字节）
"""


AES_MODE = {
    'ECB': AES.MODE_ECB,
    'CBC': AES.MODE_CBC,
    'CFB': AES.MODE_CFB,
    'OFB': AES.MODE_OFB,
    'CTR': AES.MODE_CTR,
    'OPENPGP': AES.MODE_OPENPGP,
    'CCM': AES.MODE_CCM,
    'EAX': AES.MODE_EAX,
    'GCM': AES.MODE_GCM,
    'SIV': AES.MODE_SIV,
    'OCB': AES.MODE_OCB
}


def encrypt(plaintext, key, plaintext_encode_type=None, block_size=16, mode='ECB') -> [str, bytes]:
    if mode not in AES_MODE:
        raise KeyError('aes mode 不存在')

    cipher = AES.new(key.encode('utf8'), AES_MODE[mode])
    ciphertext = cipher.encrypt(pad(plaintext.encode('utf8'), int(block_size)))

    if plaintext_encode_type == 'base64':
        return base64.b64encode(ciphertext).decode('utf8')
    elif plaintext_encode_type == 'hex':
        return binascii.b2a_hex(ciphertext).decode('utf8')
    else:
        return ciphertext


def decrypt(ciphertext, key, ciphertext_decode_type=None, block_size=16, mode='ECB'):
    if mode not in AES_MODE:
        raise KeyError('aes mode 不存在')

    if ciphertext_decode_type == 'base64':
        binary_data = base64.b64decode(ciphertext.encode('utf8'))
    elif ciphertext_decode_type == 'hex':
        binary_data = binascii.a2b_hex(ciphertext.encode('utf8'))
    else:
        binary_data = ciphertext

    decipher = AES.new(key.encode('utf8'), AES_MODE[mode])
    return unpad(decipher.decrypt(binary_data), int(block_size)).decode('utf8')


if __name__ == '__main__':
    # OBStWkqV6YnEIBVmCkC34w==
    # 3814ad5a4a95e989c42015660a40b7e3
    data = encrypt('123456', 'UTh7LJTGbo7oupjwt0/Naw==', 'hex')
    print(data)
    text1 = decrypt('OBStWkqV6YnEIBVmCkC34w==', 'UTh7LJTGbo7oupjwt0/Naw==', 'base64')
    print(text1)
    text2 = decrypt('3814ad5a4a95e989c42015660a40b7e3', 'UTh7LJTGbo7oupjwt0/Naw==', 'hex')
    print(text2)
