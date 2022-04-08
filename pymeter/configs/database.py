#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : database.py
# @Time    : 2022-04-05 17:46:28
# @Author  : Kelvin.Ye
from typing import Final

from sqlalchemy import create_engine

from pymeter.elements.element import ConfigTestElement
from pymeter.engine.interface import NoConfigMerge
from pymeter.engine.interface import NoCoroutineClone
from pymeter.engine.interface import TestCollectionListener
from pymeter.groups.context import ContextService
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class DatabaseEngine(ConfigTestElement, TestCollectionListener, NoConfigMerge, NoCoroutineClone):

    # 变量名称
    VARIABLE_NAME: Final = 'DatabaseEngine__variable_name'

    # 数据库类型
    DATABASE_TYPE: Final = 'DatabaseEngine__database_type'

    # 驱动名称
    DRIVER: Final = 'DatabaseEngine__driver'

    # 用户名称
    USERNAME: Final = 'DatabaseEngine__username'

    # 用户密码
    PASSWORD: Final = 'DatabaseEngine__password'

    # 主机
    HOST: Final = 'DatabaseEngine__host'

    # 端口
    PORT: Final = 'DatabaseEngine__port'

    # 连接串query参数
    QUERY: Final = 'DatabaseEngine__query'

    # 库名
    DATABASE: Final = 'DatabaseEngine__database'

    # 连接超时时间（ms）
    CONNECT_TIMEOUT: Final = 'DatabaseEngine__connect_timeout'

    @property
    def variable_name(self) -> str:
        return self.get_property_as_str(self.VARIABLE_NAME)

    @property
    def database_type(self) -> str:
        return self.get_property_as_str(self.DATABASE_TYPE)

    @property
    def driver(self) -> str:
        return self.get_property_as_str(self.DRIVER)

    @property
    def username(self) -> str:
        return self.get_property_as_str(self.USERNAME)

    @property
    def password(self) -> str:
        return self.get_property_as_str(self.PASSWORD)

    @property
    def host(self) -> str:
        return self.get_property_as_str(self.HOST)

    @property
    def port(self) -> str:
        return self.get_property_as_str(self.PORT)

    @property
    def query(self) -> str:
        return self.get_property_as_str(self.QUERY)

    @property
    def database(self) -> str:
        return self.get_property_as_str(self.DATABASE)

    @property
    def connect_timeout(self) -> int:
        ms = self.get_property_as_int(self.CONNECT_TIMEOUT, 10000)
        return int(ms / 1000)

    @property
    def url(self) -> str:
        """
        cx-Oracle: oracle+cx_oracle

        mysqlclient: mysql+mysqldb
        PyMySQL: mysql+pymysql
        mysql-connector-python: mysql+mysqlconnector

        psycopg2: postgresql+psycopg2
        pg8000: postgresql+pg8000

        pyodbc: mssql+pyodbc
        pymssql: mssql+pymssql
        """
        url = '{}+{}://{}:{}@{}:{}/{}'.format(
            self.database_type,
            self.driver,
            self.username,
            self.password,
            self.host,
            self.port,
            self.database
        )

        if self.query:
            url = url + '?' + self.query

        return url

    @property
    def props(self):
        return ContextService.get_context().properties

    def __init__(self):
        super().__init__()
        self.engine = None

    def collection_started(self) -> None:
        """@override"""
        log.debug(f'database:[ {self.database_type}/{self.database} ] start to connect')
        self.engine = self._connect()
        log.debug(f'database:[ {self.database_type}/{self.database} ] connected')
        self.props.put(self.variable_name, self.engine)

    def collection_ended(self) -> None:
        """@override"""
        log.debug(f'database:[ {self.database_type}/{self.database} ] start to close')
        self.engine.dispose()
        log.debug(f'database:[ {self.database_type}/{self.database} ] closed')

    def _connect(self):
        engine = create_engine(self.url, connect_args={'connect_timeout': self.connect_timeout})
        return engine
