#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : reflect
# @Time    : 2020/1/20 16:48
# @Author  : Kelvin.Ye
import pkgutil
import sys

from pymeter.utils.path_util import SRC_PATH


class Reflect:
    @staticmethod
    def for_name(class_name: str):
        """根据类名返回类的对象
        """
        return getattr(sys.modules[__name__], class_name)

    @staticmethod
    def get_name():
        """获得类的完整路径名字
        """
        pass

    @staticmethod
    def new_instance():
        """创建类的实例
        """
        pass


"""
-------如果是在同一个命名空间
clazz = globals()['classname']
instance= clazz()

------如果在其它module，先import导入该module
import module
clazz= getattr(module, 'classname')
instance = clazz()
"""

if __name__ == '__main__':
    # print(sys.modules)
    # print(getattr(sys.modules, 'Function'))
    for obj in pkgutil.walk_packages([SRC_PATH], 'pymeter.'):
        print(obj)
