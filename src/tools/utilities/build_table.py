# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

from numpy import inf

from tools.services.connection_1.connection import query_analog_data as connection_1_data
from tools.services.connection_2.connection import query_analog_data as connection_2_data

DATABASE = {"connection_1": connection_1_data, "connection_2": connection_2_data}


def get_time_sum_values(
    connection, tags, column_name, start_date, end_date, sum_values=True
) -> pd.Series:
    if isinstance(tags, str):
        tags = (tags,)
    query_data = DATABASE[connection["type"]]
    connection = connection["which"]

    data = query_data(connection, tags, start_date, end_date, 60)  # --sample every 60s
    data[data == inf] = 0
    if sum_values == True:
        data = data.sum(axis=1)
    if isinstance(data, pd.DataFrame):
        data.columns = column_name
    else:
        data = data.rename(column_name)
    data = data.asfreq("60S")
    return data


def get_zero_values(column_name, start_date, end_date):
    idx = pd.date_range(start=start_date, end=end_date, freq="T")
    values = [0.0] * len(idx)
    data = pd.DataFrame(values, index=idx, columns=[f"{column_name}"])
    return data


# Can be deleted once Titan and Comp Station data is retrievable
def extend_list(lst):
    lst = [0] * 16 + lst
    lst.append(0)
    return lst


def convert_to_zero(lst):
    lst = np.asarray(lst)
    lst[lst == inf] = 0
    lst = np.nan_to_num(lst).tolist()
    return lst
