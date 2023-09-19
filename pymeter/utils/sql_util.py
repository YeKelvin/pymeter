#!/usr/bin python3
# @File    : sql_util.py
# @Time    : 2020/2/21 11:21
# @Author  : Kelvin.Ye
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.engine.result import ResultProxy


class SQL:
    def __init__(self, url: str):
        self.url = url
        self.engine = create_engine(url)

    def execute(self, expression: str) -> tuple[Connection, ResultProxy]:
        """执行 sql

        :param expression:  sql
        :return:            sql结果集
        """
        connection = self.engine.connect()
        result_proxy = connection.execute(expression)
        return connection, result_proxy

    def select_first(self, expression: str):
        connection, result_proxy = self.execute(expression)
        rows = result_proxy.first()
        connection.close()
        return rows
