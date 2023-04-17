#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sql_sampler.py
# @Time    : 2020/2/17 15:33
# @Author  : Kelvin.Ye
import re
from collections import deque
from typing import Final

import gevent
from loguru import logger
from sqlalchemy import text
from sqlalchemy.engine import Engine
from tabulate import tabulate

from pymeter.samplers.sample_result import SampleResult
from pymeter.samplers.sampler import Sampler


class SQLSampler(Sampler):

    # 请求类型
    REQUEST_TYPE: Final = 'SQL'

    # 数据库引擎变量名称
    ENGINE_NAME: Final = 'SQLSampler__engine_name'

    # 语句
    STATEMENT: Final = 'SQLSampler__statement'

    # 查询限制结果数
    LIMIT: Final = 'SQLSampler__limit'

    # 结果变量名称
    RESULT_NAME: Final = 'SQLSampler__result_name'

    # 超时时间
    QUERY_TIMEOUT: Final = 'SQLSampler__query_timeout'

    # 查询语句正则表达式
    SELECT_PATTERN = re.compile(r'(select)(.|\n)+(from)(.|\n)*', re.IGNORECASE)

    @property
    def engine_name(self) -> str:
        return self.get_property_as_str(self.ENGINE_NAME)

    @property
    def statement(self) -> str:
        if stmt := self.get_property_as_str(self.STATEMENT):
            stmt = stmt.strip()
        return stmt

    @property
    def limit(self) -> str:
        return self.get_property_as_str(self.LIMIT, '10')

    @property
    def result_name(self) -> str:
        return self.get_property_as_str(self.RESULT_NAME, 'rows')

    @property
    def query_timeout(self) -> float:
        ms = self.get_property_as_int(self.QUERY_TIMEOUT, 10000)
        return float(ms / 1000)

    @property
    def database_engine(self) -> Engine:
        return self.props.get(self.engine_name).get('engine')

    @property
    def database_type(self) -> str:
        return self.props.get(self.engine_name).get('type')

    @property
    def props(self):
        return self.context.properties

    @property
    def variables(self):
        return self.context.variables

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_name = self.name
        result.request_data = self.statement
        result.sample_start()

        connection = None
        timeout = gevent.Timeout(1)
        timeout.start()

        try:
            connection = self.database_engine.connect()
            stmt = self.get_statement()
            logger.debug(f'sampler:[ {self.name} ] execute:[ {stmt} ]')
            if query_result := connection.execute(text(stmt)):
                result.response_data = f'rowcount={query_result.rowcount}'
                if query_result.returns_rows:
                    mappings = query_result.mappings()
                    rows = mappings.all()
                    result.response_data = '{}\n{}'.format(
                        result.response_data,
                        tabulate(rows, headers={key: key for key in mappings.keys()}, tablefmt='grid')
                    )
                    self.variables.put(self.result_name, rows)
        except gevent.Timeout:
            result.success = False
            result.response_data = 'timeout'
        except Exception as e:
            result.success = False
            result.response_data = e
            logger.exception()
        finally:
            timeout.close()
            result.sample_end()
            connection and not connection.closed and connection.close()

        return result

    def get_statement(self):
        """获取sql表达式，如果是select语句则添加限制"""
        stmt = self.statement
        if self.SELECT_PATTERN.search(stmt):
            stmt = self.add_limit(stmt)
        else:
            stmt = stmt.strip()
        return stmt

    def add_limit(self, stmt):
        """添加查询结果数限制，防止大数据结果集"""
        stmt = self.remove_comments(stmt)
        if self.database_type == 'oracle':
            stmt = f'select * from ({stmt}) t where rownum<={self.limit}'
        if self.database_type == 'mysql':
            stmt = f'select * from ({stmt}) t limit {self.limit}'
        if self.database_type == 'postgresql':
            stmt = f'select * from ({stmt}) t limit {self.limit}'
        if self.database_type == 'mssql':
            stmt = f'select top {self.limit} * from ({stmt}) t'
        return stmt

    @staticmethod
    def remove_comments(stmt) -> str:
        """删除表达式中的注释部分"""
        sql = deque()
        pre = ''
        single_quotes = False
        double_quotes = False
        single_line_comment = False
        multi_line_comment = False
        for ch in stmt:
            if ch == '#' and not single_quotes and not double_quotes:  # match '#'
                single_line_comment = True
                pre = ch
                continue
            if ch == ' ' and pre == '-' and sql[-1] == '-' and not single_quotes and not double_quotes:  # match '-- '
                single_line_comment = True
                sql.pop()
                sql.pop()
                pre = ch
                continue
            if ch == '\n' and single_line_comment and not single_quotes and not double_quotes:
                single_line_comment = False
            if ch == '*' and pre == '/' and not single_quotes and not double_quotes:  # match '/*'
                multi_line_comment = True
                sql.pop()
                pre = ch
                continue
            if ch == '/' and pre == '*' and multi_line_comment and not single_quotes and not double_quotes:  # match '*/'
                multi_line_comment = False
                pre = ch
                continue
            if single_line_comment or multi_line_comment:
                pre = ch
                continue
            if ch == "'" and pre != '\\':
                single_quotes = not single_quotes
            if ch == '"' and pre != '\\':
                double_quotes = not double_quotes
            sql.append(ch)
            pre = ch
        return ''.join(sql).strip()
