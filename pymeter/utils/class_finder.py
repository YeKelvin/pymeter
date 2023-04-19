#!/usr/bin python3
# @File    : class_finder
# @Time    : 2020/1/20 15:17
# @Author  : Kelvin.Ye


class ClassFinder:
    @staticmethod
    def find_subclasses(clazz, inner=False):
        """获取 clazz的所有子类
        """
        subclasses = {}
        for subclass in clazz.__subclasses__():
            if subclass.__name__ not in subclasses:
                subclasses[subclass.__name__] = subclass
            if inner:
                subclasses.update(ClassFinder.find_subclasses(subclass))
        return subclasses
