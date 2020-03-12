#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : setup.py
# @Time    : 2020/3/12 10:57
# @Author  : Kelvin.Ye
import os
from setuptools import setup

from setuptools import find_packages
from sendanywhere import __version__

with open(os.path.join('.', 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='send-anywhere',
    version=__version__,
    description='Json script execution module.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='',
    url='',
    author='Kelvin.Ye',
    author_email='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        'click==7.0',
        'orjson==2.1.4',
        'jsonpath==0.82',
        'gevent==1.4.0',
        'requests==2.22.0',
        'flask==1.1.1',
        'sqlalchemy==1.3.13',
        'sshtunnel==0.1.5',
    ],
    tests_require=[
        'pytest==5.3.3',
    ],
    entry_points={}
)
