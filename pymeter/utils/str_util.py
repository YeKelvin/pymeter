#!/usr/bin python3
# @File    : str_util
# @Time    : 2020/1/19 10:01
# @Author  : Kelvin.Ye


def substitute(source: str, pattern: str, sub: str) -> str:
    substr = []
    start = 0
    length = len(pattern)
    while True:
        index = source.find(pattern, start)
        if index >= start:
            substr.append(source[start:index])
            substr.append(sub)
            start = index + length
        else:
            break
    substr.append(source[start:])
    return ''.join(substr)
