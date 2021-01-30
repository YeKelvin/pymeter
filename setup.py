#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : setup.py
# @Time    : 2020/3/12 10:57
# @Author  : Kelvin.Ye
import pathlib

from setuptools import setup, find_packages

from sendanywhere import __version__

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name='send-anywhere',
    version=__version__,
    description='Json script execution module',
    long_description=README,
    long_description_content_type="text/markdown",
    url='',
    license='',
    author='Kelvin.Ye',
    author_email='testmankelvin@163.com',
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
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
    extras_require={
        'test': [
            'pytest==5.3.3',
        ]
    },
    entry_points={},
    python_requires=">=3.6",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ]
)
