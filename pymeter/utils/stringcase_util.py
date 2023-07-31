#!/usr/bin python3
# @File    : named_util.py
# @Time    : 2023-07-31 10:09:09
# @Author  : Kelvin.Ye
import re


snakecase_step1_re = re.compile('(.)([A-Z][a-z]+)')
snakecase_step2_re = re.compile('([a-z0-9])([A-Z])')

def snakecase(name):
    """蛇形命名

    stringcase.snakecase('foo_bar_baz') # => "foo_bar_baz"
    stringcase.snakecase('FooBarBaz') # => "foo_bar_baz"
    """
    if not name:
        return name

    name = snakecase_step1_re.sub(r'\1_\2', name)
    return snakecase_step2_re.sub(r'\1_\2', name).lower()


def camelcase(name):
    """小驼峰命名

    stringcase.camelcase('foo_bar_baz') # => "fooBarBaz"
    stringcase.camelcase('FooBarBaz') # => "fooBarBaz"
    """
    if not name:
        return name

    name = name.replace('_','-')
    lst = name.split('-')
    for i in range(len(lst)):
        if i == 0:
            continue
        else:
            lst[i] = lst[i].capitalize()

    return ''.join(lst)


def pascalcase(name):
    """大驼峰命名"""
    ...
