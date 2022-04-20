# -*- coding: utf-8 -*-
import datetime as dt

import numpy as np
import pandas as pd

from numpy import inf
from scipy.integrate import cumtrapz

from tools.algorithms.production_filtering import infer_prod_rate
from tools.utilities.tags import GetTags
from tools.utilities.build_table import get_time_sum_values, get_zero_values

CONNECTION = GetTags().connection
CONNECTION_TYPE = GetTags().connection_type
TRUCKED = GetTags().trucked


def product_calculations(data):
    filtered_measurements = infer_prod_rate(data).reshape(-1, 3)
    infered_fillrate = filtered_measurements[:, 2]
    scfm = (data.inlet_flowrate * 1000) / 1440
    per_inlet_values = infered_fillrate / scfm
    per_inlet_values[per_inlet_values < 0] = 0
    per_inlet_values[per_inlet_values == inf] = 0

    results = []
    for result in infered_fillrate:
        if result < 0:
            result = 0
        results.append(result)
    cumulative_values = np.cumsum(results)
    return per_inlet_values, cumulative_values


def calculate_product_totals(location, data):
    if TRUCKED(location) == "YES":
        product_total = data.cumulative_product.iloc[-1]
        product_pumped = data.cumulative_pumped.iloc[-1]
    elif CONNECTION_TYPE(location) == "wonderware":
        product_total = data.cumulative_product.iloc[-1] / 42
        product_pumped = data.cumulative_pumped.iloc[-1] / 42
    else:
        product_total = data.cumulative_product.iloc[-1] / 42
        product_pumped = data.cumulative_pumped.iloc[-1]
    return product_total, product_pumped


def calculate_cumulative_flows(column, time_adjustment):
    return cumtrapz(column, initial=0) * time_adjustment


def calculate_cumulative_tank_volumes(column, time_adjustment):
    return (
        cumtrapz((column - column.shift(periods=1)).fillna(0), initial=0)
        * time_adjustment
    )


def calculate_cumulative_trucked_tank_volumes(column, time_adjustment):
    level_changes = (column - column.shift(periods=1)).fillna(0)
    adj_changes = np.where(level_changes < 0, 0, level_changes)
    return cumtrapz(adj_changes, initial=0) * time_adjustment


def get_location_data(
    location,
    tags: list,
    columns: list,
    start_date: dt,
    end_date: dt,
    trucked,
    sum_values=True,
):
    all_tbls = []

    for tag, col in zip(tags, columns):
        if sum_values == True:
            tbl = get_time_sum_values(
                CONNECTION(location), tag, col, start_date, end_date
            )
        else:
            tbl = get_time_sum_values(
                CONNECTION(location), tag, col, start_date, end_date, sum_values=False
            )
        all_tbls.append(tbl)
    if trucked == "YES":
        condensate_flowrate_data = get_zero_values("product_flowrate", start_date, end_date)
        all_tbls.append(condensate_flowrate_data)

    location_data = pd.concat(all_tbls, axis=1, sort=True)
    location_data = location_data.fillna(0)

    return location_data
