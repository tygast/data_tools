# -*- coding: utf-8 -*-
from typing import Tuple

import numpy as np
import pandas as pd

from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import KalmanFilter


def measurement_noise(data):
    return [np.array([[100, 0], [0, 1]]) for _ in range(len(data))]


def process_control(data):
    us = [None] * len(data)
    dpumprate = zip(data.itertuples(), data.shift().itertuples())
    next(dpumprate)
    for i, (current_row, prev_row) in enumerate(dpumprate, 1):
        us[i] = np.array(
            [0, current_row.product_flowrate - prev_row.product_flowrate, 0]
        ).reshape(-1, 1)
    return us


def infer_prod_rate(data):
    kf = KalmanFilter(dim_x=3, dim_z=2, dim_u=1)
    kf.x = np.array(
        [
            data.product_tank_volume.iloc[0],
            data.product_flowrate.iloc[0],
            data.product_flowrate.sum() / 1440,
        ]
    ).reshape(-1, 1)
    kf.F = np.array([[1, -1, 1], [0, 1, 0], [0, 0, 1]])
    kf.B = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
    kf.H = np.array([[1, 0, 0], [0, 1, 0]])
    kf.P *= 500
    kf.Q = np.array([[100, -1, 1], [-1, 1, 0], [1, 0, 1]])
    rs = measurement_noise(data)
    us = process_control(data)
    zs = data[["product_tank_volume", "product_flowrate"]].values.reshape(-1, 2, 1)
    mu, cov, _, _ = kf.batch_filter(zs=zs, Rs=rs, us=us)
    x, _, _, _ = kf.rts_smoother(mu, cov)
    return x


def infer_tank_level(data: pd.Series) -> Tuple[np.ndarray, float]:
    kf = KalmanFilter(dim_x=2, dim_z=1)
    kf.H = np.array([[1, 0]])
    kf.P *= 500
    kf.R = 100
    xs = []
    mds = []
    current_records = data.iteritems()
    next_records = data.iteritems()
    init_ts, init_reading = next(next_records)
    kf.x = np.array([init_reading, 0]).reshape(-1, 1)
    xs.append(np.copy(kf.x))
    mds.append(0)
    for (c_ts, c_level), (n_ts, n_level) in zip(current_records, next_records):
        dt = (n_ts - c_ts).total_seconds() / 60

        kf.F = np.array([[1, dt], [0, 1]])
        kf.Q = Q_discrete_white_noise(dim=2, dt=dt, var=0.01)
        kf.predict()
        kf.update(n_level)
        xs.append(np.copy(kf.x))
        mds.append(kf.mahalanobis)
    return xs, mds
