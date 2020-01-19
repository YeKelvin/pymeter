#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : parser
# @Time    : 2020/1/19 16:17
# @Author  : Kelvin.Ye


class FunctionParser:

    @staticmethod
    def compile_str(source: str):
        buffer = []
        previous = ''
        for current in source:
            if current == '\\':
                previous = current
                # Keep '\' unless it is one of the escapable chars '$' ',' or '\'
                #  N.B. This method is used to parse function parameters, so must treat ',' as special
                if current != '$' and current != ',' and current[0] != '\\':
                    buffer.append(previous)
                previous = ''
                buffer.append(current)
            elif current == '{' and previous == '$':  # found "${"
                # buffer.deleteCharAt(buffer.length() - 1)
                pass
            else:
                buffer.append(current)
                previous = current

    @staticmethod
    def make_function(self, str_reader: str):
        buffer = []
        previous = ''
        for current in str_reader:
            if current == '\\':
                previous = ''
                buffer.append(current)
            elif current[0] == '(' and previous != '':
                pass

    @staticmethod
    def parse_params(self):
        pass
