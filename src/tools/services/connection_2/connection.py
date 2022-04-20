# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime as dt

from typing import List

import pandas as pd

from sqlalchemy import and_, sql
from sqlalchemy.exc import OperationalError

from tools.databases.connections import engines

from .location_a.tables import t_AnalogHistory as location_a_analog
from .location_b.tables import t_AnalogHistory as location_b_analog
from .location_c.tables import t_AnalogHistory as location_c_analog
from .location_d.tables import t_AnalogHistory as location_d_analog
from .location_e.tables import t_AnalogHistory as location_e_analog
from .location_f.tables import t_AnalogHistory as location_f_analog


historian = {
    "location_a": (engines("marshall_history_engine"), location_a_analog),
    "location_b": (engines("milton_history_engine"), location_b_analog),
    "location_c": (engines("shiner_history_engine"), location_c_analog),
    "location_d": (engines("smiley_history_engine"), location_d_analog),
    "location_e": (engines("lyssy_history_engine"), location_e_analog),
    "location_f": (engines("titan_history_engine"), location_f_analog),
}


def query_statement(table, tags, start_datetime, end_datetime, sample_freq):
    """Make query statement to get values for tags.

    Params:
        table: which table to use to get tags from
        tags: which tags to get values for
        start_datetime: earliest start_date
        end_datetime: latest datetime to get values for
        sample_freq: number of seconds between samples
            connection_2 will interpolate 

    Returns:
        sqlalchemy created query statement

    """
    statement = sql.select([table.c.TagName, table.c.Value, table.c.DateTime]).where(
        and_(
            table.c.DateTime > start_datetime,
            table.c.DateTime < end_datetime,
            table.c.TagName.in_(tags),
            table.c.wwRetrievalMode == "Cyclic",
            table.c.wwResolution
            == 1000 * sample_freq,  # convert from seconds to milliseconds
        )
    )
    return statement


def query_analog_data(
    which_historian: str,
    tags: List[str],
    start_datetime: dt.datetime,
    end_datetime: dt.datetime,
    sample_freq: float = 1,
) -> pd.DataFrame:
    """Query the historian for the tag values.

    Params:
        which_historian: which historian to pull from
            options are query_functions.historian.keys()
        tags: tag name or tuple of tag names in historian to query for
        start_datetime: earliest datetime to go to
        end_datetime: latest datetime to go to
        sample_freq: timespan between recordings in seconds
            historian will interpolate or fill in data if it doesn't
            exist for every time point

    Returns:
        dataframe: index is datetimes
            columns are tags names
    """
    engine, table = historian[which_historian]
    statement = query_statement(table, tags, start_datetime, end_datetime, sample_freq)
    try:
        data = pd.read_sql(statement, engine)
    except OperationalError as err:
        raise LookupError(
            f"Could not retrieve data for {tags} from {which_historian} connnection: {engine!r}"
        ) from err
    data.columns = data.columns.str.lower()
    data["tagname"] = data["tagname"].str.lower()
    data["datetime"] = pd.to_datetime(data["datetime"])
    data["value"] = data["value"].fillna(0)
    data = data.pivot_table(
        index="datetime", columns="tagname", values="value", dropna=False
    )
    data = data.asfreq("60S")
    data.index = pd.DatetimeIndex(data.index, freq=f"{sample_freq}s", name="datetime")
    data = data.fillna(data.rolling(window=20, center=True, min_periods=20).mean())
    if which_historian == "titan":
        for tag in tags:
            if "DischargeROC" in tag:
                data[str(tag.lower())] = data[str(tag.lower())] / 1000

    return data
