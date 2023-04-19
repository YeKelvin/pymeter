#!/usr/bin python3
# @File    : str_util_test
# @Time    : 2020/1/19 10:55
# @Author  : Kelvin.Ye
from pymeter.utils.str_util import substitute


def test_substitute():
    source = 'aabbcc'
    pattern = 'bb'
    sub = '##'
    substr = substitute(source, pattern, sub)
    print(f'substr={substr}')
    assert 'aa##cc' == substr
