#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : class_finder
# @Time    : 2020/1/20 15:17
# @Author  : Kelvin.Ye
from sendanywhere.functions import Function


class ClassFinder:
    @staticmethod
    def find_subclasses(clazz, inner=False):
        """
        获取父类的所有子类
        """
        subclasses = {}
        for subclass in clazz.__subclasses__():
            if subclass.__name__ not in subclasses:
                subclasses[subclass.__name__] = subclass
            if inner:
                subclasses.update(ClassFinder.find_subclasses(subclass))
        return subclasses


if __name__ == '__main__':
    classes = ClassFinder.find_subclasses(Function)
    print(classes)
