#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sql_sampler.py
# @Time    : 2020/2/17 15:33
# @Author  : Kelvin.Ye
import traceback
from typing import Final

import gevent
from sqlalchemy import text
from sqlalchemy.engine import Engine

from pymeter.samplers.sample_result import SampleResult
from pymeter.samplers.sampler import Sampler
from pymeter.utils.log_util import get_logger


log = get_logger(__name__)


class SQLSampler(Sampler):

    # 数据库引擎变量名称
    ENGINE_NAME: Final = 'SQLSampler__engine_name'

    # 语句
    STATEMENT: Final = 'SQLSampler__statement'

    # 结果变量名称
    RESULT_NAME: Final = 'SQLSampler__result_name'

    # 超时时间
    QUERY_TIMEOUT: Final = 'SQLSampler__query_timeout'

    @property
    def properties(self):
        return self.context.properties

    @property
    def variables(self):
        return self.context.variables

    @property
    def engine(self) -> Engine:
        engine_name = self.get_property_as_str(self.ENGINE_NAME)
        return self.properties.get(engine_name)

    @property
    def statement(self) -> str:
        return self.get_property_as_str(self.STATEMENT)

    @property
    def result_name(self) -> str:
        return self.get_property_as_str(self.RESULT_NAME)

    @property
    def query_timeout(self) -> float:
        ms = self.get_property_as_int(self.QUERY_TIMEOUT)
        return float(ms / 1000)

    def sample(self) -> SampleResult:
        result = SampleResult()
        result.sample_name = self.name
        result.request_data = self.statement
        result.sample_start()

        # noinspection PyBroadException
        try:
            with self.engine.connect() as connection:
                with gevent.Timeout(self.query_timeout, False):
                    result = connection.execute(text(self.statement))
                    if result:
                        self.variables.put(self.result_name, result)
        except Exception:
            result.success = False
            result.response_data = traceback.format_exc()
        finally:
            result.sample_end()

        return result
