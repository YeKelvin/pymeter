#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : property.py
# @Time    : 2020/2/16 14:16
# @Author  : Kelvin.Ye
from typing import Dict
from typing import Iterable
from typing import List

from pymeter.groups.context import ContextService
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class PyMeterProperty:
    def __init__(self, name: str, value: any = None):
        self.name = name
        self.value = value
        self._running_version = False

    @property
    def running_version(self):
        return self._running_version

    @running_version.setter
    def running_version(self, running):
        self._running_version = running

    def get_str(self) -> str:
        raise NotImplementedError

    def get_int(self) -> int:
        raise NotImplementedError

    def get_float(self) -> float:
        raise NotImplementedError

    def get_bool(self) -> bool:
        raise NotImplementedError

    def get_obj(self) -> object:
        raise NotImplementedError

    def recover_running_version(self, owner) -> None:
        raise NotImplementedError


class BasicProperty(PyMeterProperty):

    def __init__(self, name: str, value=None):
        super().__init__(name, value)
        self.saved_value = None

    def get_str(self) -> str:
        return str(self.value)

    def get_int(self) -> int:
        value = self.get_str()
        return int(value) if value else 0

    def get_float(self) -> float:
        value = self.get_str()
        return float(value) if value else 0.00

    def get_bool(self) -> bool:
        value = self.get_str()
        return True if value.lower() == 'true' else False

    def get_obj(self) -> object:
        return self.value

    @property
    def running_version(self):
        return self._running_version

    @running_version.setter
    def running_version(self, running):
        PyMeterProperty.running_version = running
        if running:
            self.saved_value = self.value
        else:
            self.saved_value = None

    def recover_running_version(self, owner) -> None:
        if self.saved_value is not None:
            self.value = self.saved_value

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class NoneProperty(PyMeterProperty):

    def __init__(self, name: str):
        super().__init__(name, None)

    def get_str(self) -> str:
        return ''

    def get_int(self) -> int:
        return 0

    def get_float(self) -> float:
        return 0.00

    def get_bool(self) -> bool:
        return False

    def get_obj(self) -> None:
        return None

    def recover_running_version(self, owner) -> None:
        ...


class MultiProperty(PyMeterProperty):

    @property
    def running_version(self):
        return self._running_version

    @running_version.setter
    def running_version(self, running):
        self._running_version = running
        for prop in self.iterator():
            prop.running_version = running

    def iterator(self) -> Iterable:
        raise NotImplementedError

    def remove(self, property):
        raise NotImplementedError

    def recover_running_version_of_subelements(self, owner):
        """
        Args:
            owner (TestElement):  TestElement
        """
        for prop in self.iterator()[:]:
            if owner.is_temporary(prop):
                self.remove(prop)
            else:
                if isinstance(prop, PyMeterProperty):
                    prop.recover_running_version(owner)
                else:
                    prop.recover_running_version()  # prop: TestElement


class CollectionProperty(MultiProperty):

    def __init__(self, name: str, value: List[PyMeterProperty] = []):
        super().__init__(name, value)
        self.saved_value = None

    def get_str(self) -> str:
        return str(self.value)

    def get_bool(self) -> bool:
        return bool(self.value)

    def get_obj(self) -> List:
        return self.value

    def remove(self, prop) -> None:
        self.value.remove(prop)

    def set(self, prop) -> None:
        self.value.append(prop)

    def get(self, index) -> PyMeterProperty:
        return self.value[index]

    def iterator(self) -> Iterable:
        return self.value

    @property
    def running_version(self):
        return self._running_version

    @running_version.setter
    def running_version(self, running):
        MultiProperty.running_version = running
        if running:
            self.saved_value = self.value
        else:
            self.saved_value = None

    def recover_running_version(self, owner) -> None:
        if self.saved_value is not None:
            self.value = self.saved_value
        self.recover_running_version_of_subelements(owner)


class ElementProperty(MultiProperty):

    def __init__(self, name: str, value):
        super().__init__(name, value)
        self.saved_value = None

    def get_str(self) -> str:
        return str(self.value)

    def get_bool(self) -> bool:
        return bool(self.value)

    def get_obj(self):
        return self.value

    def remove(self, prop) -> None:
        self.value.remove_property(prop.name)

    def iterator(self) -> Iterable:
        return self.value.property_iterator()

    @property
    def running_version(self):
        return self._running_version

    @running_version.setter
    def running_version(self, running):
        MultiProperty.running_version = running
        self.value.running_version = running
        if running:
            self.saved_value = self.value
        else:
            self.saved_value = None

    def recover_running_version(self, owner) -> None:
        if self.saved_value is not None:
            self.value = self.saved_value
        self.value.recover_running_version()


class DictProperty(MultiProperty):

    def __init__(self, name: str, value: Dict[str, PyMeterProperty] = {}):
        super().__init__(name, value)
        self.saved_value = None

    def get_str(self) -> str:
        return str(self.value)

    def get_bool(self) -> bool:
        return bool(self.value)

    def get_obj(self) -> Dict:
        return self.value

    def remove(self, prop) -> None:
        self.value.pop(prop.name)

    def iterator(self) -> Iterable:
        return self.value.values()

    @property
    def running_version(self):
        return self._running_version

    @running_version.setter
    def running_version(self, running):
        MultiProperty.running_version = running
        if running:
            self.saved_value = self.value
        else:
            self.saved_value = None

    def recover_running_version(self, owner) -> None:
        if self.saved_value is not None:
            self.value = self.saved_value
        self.recover_running_version_of_subelements(owner)


class FunctionProperty(PyMeterProperty):

    def __init__(self, name: str, function):
        super().__init__(name)
        self.function = function  # pymeter.engine.values.CompoundVariable
        self.cache_value = None
        self.test_iteration = -1

    @property
    def ctx(self):
        return ContextService.get_context()

    def get_raw(self):
        return self.function.raw_parameters

    def get_str(self):
        iter = self.ctx.variables.iteration if self.ctx.variables else -1

        if iter < self.test_iteration:
            self.test_iteration = -1

        if iter > self.test_iteration or self.cache_value is None:
            log.debug('executing function in FunctionProperty')
            self.test_iteration = iter
            self.cache_value = self.function.execute()

        return self.cache_value

    def recover_running_version(self, owner) -> None:
        self.cache_value = None
