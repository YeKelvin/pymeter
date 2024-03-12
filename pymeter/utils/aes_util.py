#!/usr/bin python3
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


AES_MODES = {
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

BLOCK_SIZES = {
    '128': 16,
    '192': 24,
    '256': 32
}


def encrypt(data, key, mode='ECB', size='128', iv=None, encoding=None) -> str | bytes:
    if mode not in AES_MODES:
        raise KeyError('aes mode 不存在')

    cipher = AES.new(key.encode('utf8'), AES_MODES[mode], iv)
    bdata = pad(data.encode('utf8'), int(BLOCK_SIZES[size]))
    ciphertext = cipher.encrypt(bdata)

    if encoding == 'base64':
        return base64.b64encode(ciphertext).decode('utf8')
    elif encoding == 'hex':
        return binascii.b2a_hex(ciphertext).decode('utf8')
    else:
        return ciphertext


def decrypt(ciphertext, key, mode='ECB', size='128', iv=None, encoding=None):
    if mode not in AES_MODES:
        raise KeyError('aes mode 不存在')

    if encoding == 'base64':
        binary_data = base64.b64decode(ciphertext.encode('utf8'))
    elif encoding == 'hex':
        binary_data = binascii.a2b_hex(ciphertext.encode('utf8'))
    else:
        binary_data = ciphertext

    decipher = AES.new(key.encode('utf8'), AES_MODES[mode], iv)
    return unpad(decipher.decrypt(binary_data), int(BLOCK_SIZES[size])).decode('utf8')
