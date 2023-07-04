#!/usr/bin python3
# @File    : properties.py
# @Time    : 2023-07-04 16:25:40
# @Author  : Kelvin.Ye


class Properties(dict):

    def put(self, key: str, value: any) -> None:
        self[key] = value

    def has(self, key: str) -> bool:
        return key in self
