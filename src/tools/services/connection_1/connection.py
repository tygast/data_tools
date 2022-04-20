# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime as dt

from typing import List

import numpy as np
import pandas as pd

from pycygnet.cx_vhs import CxValueIterator



def add_noise(column, noise):
    noise = np.random.normal(0, noise, len(column)).tolist()
    noisy_vals = []
    for val, noise in zip(column, noise):
        if val == 0:
            noisy_vals.append(0)
        else:
            noisy_vals.append(val + noise)
    noisy_vals = np.asarray(noisy_vals)
    return noisy_vals


def query_analog_data(
    site: str,
    tags: List[str],
    start_date: dt.datetime,
    end_date: dt.datetime,
    sample_freq=1,
):

    dataframes = []

    for tag in tags:
        hist_iterator = CxValueIterator(
            site, tag_string=tag, earliest=start_date, latest=end_date
        )
        values = [(val.datetime, val.value) for val in hist_iterator]

        query_range = pd.date_range(start=start_date, end=end_date, freq="T")
        blank_data = pd.DataFrame(
            np.nan, columns=["datetime", "value"], index=range(0, len(query_range))
        )
        blank_data["datetime"] = query_range

        data = pd.DataFrame(values, columns=["datetime", "value"])
        data["datetime"] = pd.to_datetime(data["datetime"], format="%Y-%m-%d %H:%M")
        data["datetime"] = data.datetime.map(
            lambda x: x.replace(second=0, microsecond=0)
        ).drop_duplicates(keep="last")
        data = data.dropna(subset=["datetime"])
        if "RATE" in tag or "GRATE" in tag:
            data = pd.merge_ordered(blank_data, data, on="datetime")
            data = data.ffill(limit=14)
        elif "PRODUCT" in tag:
            data = pd.merge_ordered(blank_data, data, on="datetime")
            data = data.ffill().bfill()
        elif (
            "INLET" in tag
            or "FUEL" in tag
            or "DISCHARGE" in tag
        ):
            data = pd.merge_ordered(blank_data, data, on="datetime")
            data["value_y"] = data.value_y / 1000
            data = data.ffill().bfill()
            if "FUEL" in tag:
                data["value_y"] = add_noise(data.value_y.values.tolist(), 0.02)
            else:
                data["value_y"] = add_noise(data.value_y.values.tolist(), 0.2)
        elif "PSI" in tag:
            data = pd.merge_ordered(
                blank_data, data, fill_method="ffill", on="datetime"
            )
            data["value_y"] = add_noise(data.value_y.values.tolist(), 0.3)
        else:
            data = pd.merge_ordered(
                blank_data, data, fill_method="ffill", on="datetime"
            )
        data = data.set_index("datetime")
        data["tagname"] = tag.split(":")[-1].lower()
        data = data.pivot(columns="tagname", values="value_y")
        data.drop(data.index[:1], inplace=True)
        data.columns = data.columns.str.lower()
        dataframes.append(data.copy())

    all_data = pd.concat(dataframes, join="inner", axis=1, sort=True)
    all_data = all_data.dropna(how="any")
    return all_data
