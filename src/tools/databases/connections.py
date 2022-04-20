# -*- coding: utf-8 -*-
from __future__ import annotations

import urllib

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

import cx_Oracle

TIMEOUT_SECONDS = 60


class Engines:
    def __init__(self):
        self.engines = {}

    def __getitem__(self, key):
        return self.engines[key]

    def __setitem__(self, key, item):
        self.engines[key] = item

    def __call__(self, arg):
        return self.engines[arg]


engines = Engines()


def new_engine(func):
    engines[func.__name__] = func()
    return func


@new_engine
def history_engine_a() -> Engine:
    """
    Returns:
        database connection engine to Location A historian database
        meant to be used from Engines
         
    Example:
        >>> engine = Engines('history_engine_a')
    """
    _params = urllib.parse.quote(
        "DRIVER={SQL Server};SERVER=DATABASE_A_NAME.company.com;DATABASE=DATABASE_A;UID=user_name;PWD=password"
    )

    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={_params!s}", pool_recycle=TIMEOUT_SECONDS
    )


@new_engine
def history_engine_b() -> Engine:
    """
    Returns:
        database connection engine to Location B historian database
        meant to be used from Engines
         
    Example:
        >>> engine = Engines('history_engine_b')
    """
    _params = urllib.parse.quote(
        "DRIVER={SQL Server};SERVER=DATABASE_B_NAME.company.com;DATABASE=DATABASE_B;UID=user_name;PWD=password"
    )

    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={_params!s}", pool_recycle=TIMEOUT_SECONDS
    )


@new_engine
def history_engine_c() -> Engine:
    """
    Returns:
        database connection engine to Location C historian database
        meant to be used from Engines
         
    Example:
        >>> engine = Engines('history_engine_c')
    """
    _params = urllib.parse.quote(
        "DRIVER={SQL Server};SERVER=DATABASE_C_NAME.company.com;DATABASE=DATABASE_C;UID=user_name;PWD=password"
    )

    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={_params!s}", pool_recycle=TIMEOUT_SECONDS
    )


@new_engine
def history_engine_d() -> Engine:
    """
    Returns:
        database connection engine to Location D historian database
        meant to be used from Engines
         
    Example:
        >>> engine = Engines('history_engine_d')
    """
    _params = urllib.parse.quote(
        "DRIVER={SQL Server};SERVER=DATABASE_D_NAME.company.com;DATABASE=DATABASE_D;UID=user_name;PWD=password"
    )

    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={_params!s}", pool_recycle=TIMEOUT_SECONDS
    )


@new_engine
def history_engine_e() -> Engine:
    """
    Returns:
        database connection engine to Location E historian database
        meant to be used from Engines
         
    Example:
        >>> engine = Engines('history_engine_e')
    """
    _params = urllib.parse.quote(
        "DRIVER={SQL Server};SERVER=DATABASE_E_NAME.company.com;DATABASE=DATABASE_E;UID=user_name;PWD=password"
    )

    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={_params!s}", pool_recycle=TIMEOUT_SECONDS
    )


@new_engine
def history_engine_f() -> Engine:
    """
    Returns:
        database connection engine to Location F historian database
        meant to be used from Engines
         
    Example:
        >>> engine = Engines('history_engine_f')
    """
    _params = urllib.parse.quote(
        "DRIVER={SQL Server};SERVER=DATABASE_F_NAME.company.com;DATABASE=DATABASE_F;UID=user_name;PWD=password"
    )

    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={_params!s}", pool_recycle=TIMEOUT_SECONDS
    )
