#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : setup.py
# @Time    : 2021/12/17 14:59
# @Author  : Kelvin.Ye
from setuptools import setup


setup(
    name="pymeter",
    version="0.1.0",
    description="",
    author="Kelvin.Ye",
    author_email="testmankelvin@163.com",
    url="https://github.com/YeKelvin/pymeter.git",
    packages=['pymeter'],
    install_requires=[
        'jsonpath==0.82',
        'orjson==3.6.5',
        'xmltodict==0.12.0',
        'sqlalchemy==1.4.28',
        'cx-Oracle==8.3.0',
        'sshtunnel==0.4.0',
        'pycryptodome==3.12.0',
        'gevent==21.8.0',
        'python-socketio==5.5.0',
        'requests==2.26.0',
        'flask==2.0.2',
        'flask-socketio==5.1.1',
        'pytypes==1.0b9'
    ]
)
