# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime as dt

from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from scipy.signal import find_peaks, peak_widths

from .production_filtering import infer_tank_level

pd.options.mode.chained_assignment = None


@dataclass
class TankChanges:
    start_time: Optional[dt.datetime] = None
    start_level: Optional[float] = None
    forward_md: Optional[float] = None
    end_time: Optional[dt.datetime] = None
    end_level: Optional[float] = None
    backward_md: Optional[float] = None

    @property
    def volume_differnce(self):
        return self.start_level - self.end_level


class EliminateFalseReadings:
    strategies = []

    def __init__(self):
        self.strategy = None

    @classmethod
    def register(cls, strategy: "FalseReadingStrategy"):
        cls.strategies.append(strategy())
        return strategy

    def eliminate(self, readings):
        for strategy in self.strategies:
            readings = strategy.eliminate(readings)
        return readings


@EliminateFalseReadings.register
class FalseReadingStrategy:
    def eliminate(self, readings: List[TankChanges]) -> List[TankChanges]:
        return NotImplemented


@EliminateFalseReadings.register
class TooMany(FalseReadingStrategy):
    def eliminate(self, readings: List[TankChanges]):
        return [TankChanges()]


@EliminateFalseReadings.register
class FillReadings(FalseReadingStrategy):
    def eliminate(self, readings: List[TankChanges]):
        valid_readings = []
        for reading in readings:
            if reading.start_level is None:
                continue
            if reading.end_level is None:
                continue
            if reading.start_level > reading.end_level:
                valid_readings.append(reading)
        if not valid_readings:
            valid_readings.append(TankChanges())
        return valid_readings


@EliminateFalseReadings.register
class NotEnoughLevelChange(FalseReadingStrategy):
    min_level_change = 3

    def eliminate(self, readings: List[TankChanges]):
        valid_readings = []
        for reading in readings:
            if reading.start_level is None:
                continue
            if reading.end_level is None:
                continue
            if (reading.start_level - reading.end_level) >= self.min_level_change:
                valid_readings.append(reading)
        if not valid_readings:
            valid_readings.append(TankChanges())
        return valid_readings


@EliminateFalseReadings.register
class TimesNotAligned(FalseReadingStrategy):
    def eliminate(self, readings: List[TankChanges]):
        valid_readings = []
        for reading in readings:
            if reading.start_time is None:
                continue
            if reading.end_time is None:
                continue
            if reading.end_time > reading.start_time:
                valid_readings.append(reading)
        if not valid_readings:
            valid_readings.append(TankChanges())
        return valid_readings


@EliminateFalseReadings.register
class HighNoise(FalseReadingStrategy):
    mean_md = 0.2
    std_md = 0.1

    def eliminate(self, readings: List[TankChanges]) -> List[TankChanges]:
        valid_readings = []
        if not readings:
            return [TankChanges()]
        for reading in readings:

            if (reading.foward_md is not None) and (
                reading.foward_md > (mean_md + std_md)
            ):
                valid_readings.append(reading)
        if not valid_readings:
            valid_readings.append(TankChanges)
        return valid_readings


def level_diff(fwd_level, bkwd_level):
    if fwd_level > bkwd_level:
        fill_amount = fwd_level - bkwd_level
    else:
        fill_amount = 0
    return fill_amount


def peak_locations(data, column_1, column_2):
    peaks, _ = find_peaks(
        data[column_1], height=(0.8, 40), prominence=0.8, distance=15, width=(1.2, 10)
    )
    widths = peak_widths(data[column_1], peaks)
    all_peaks = []
    peak_times = []
    for i, j in zip(peaks, widths[0]):
        if j < 10:
            peak = data.loc[data[column_2] == i][column_1].values[0]
            when = data.loc[data[column_2] == i].index

            all_peaks.append(peak)
            peak_times.append(when[0])
    return all_peaks, peak_times


def first_peak_minimum(data, column, peak_times, direction=None):
    all_mins = []
    min_locs = []

    for i in peak_times:
        current_row = data.loc[i::direction, column].items()
        next_row = iter(data.loc[i::direction, column].items())
        next(next_row)
        for (curr_index, curr_value), (next_index, next_value) in zip(
            current_row, next_row
        ):
            if curr_value < 1:
                try:
                    if curr_value <= next_value and curr_value < 0.1:
                        md_min = curr_value
                        min_idx = curr_index
                        all_mins.append(md_min)
                        min_locs.append(min_idx)
                        break
                except KeyError:
                    continue
    return all_mins, min_locs


def find_tank_levels(data, column_2, column_3, peak_min_times):
    levels = []
    row_nums = []
    for i in peak_min_times:
        levels.append(data.loc[i, column_3])
        row_nums.append(data.loc[i, column_2])
    return levels, row_nums


def make_values_dict(peak, peak_time, peak_min, peak_min_time, level, row_num):
    values_dict = {}
    values_dict["peak"] = peak
    values_dict["peak_time"] = peak_time
    values_dict["peak_min"] = peak_min
    values_dict["peak_min_time"] = peak_min_time
    values_dict["level"] = level
    values_dict["row_num"] = row_num
    return values_dict


def find_md_stuff(data, column_1, column_2, column_3, direction=None):
    peaks, peak_times = peak_locations(data, column_1, column_2)

    peak_mins, peak_min_times = first_peak_minimum(
        data, column_1, peak_times, direction
    )

    levels, row_nums = find_tank_levels(data, column_2, column_3, peak_min_times)

    all_values = []
    for values in zip(peaks, peak_times, peak_mins, peak_min_times, levels, row_nums):
        value_dict = make_values_dict(
            values[0], values[1], values[2], values[3], values[4], values[5]
        )
        all_values.append(value_dict)

    return all_values


def eliminate_false_readings(
    fwd_values, bkwd_values
):  
    valid_fwd_values = []
    valid_bkwd_values = []
    for i, j in zip(fwd_values, bkwd_values):
        if i["level"] > j["level"] and (i["level"] - j["level"]) > 3:
            valid_fwd_values.append(i)
            valid_bkwd_values.append(j)

    if valid_fwd_values == [] and valid_bkwd_values == []:
        valid_fwd_values = [
            {
                "peak": 0,
                "peak_time": 0,
                "peak_min": 0,
                "peak_min_time": 0,
                "level": 0,
                "row_num": 0,
            }
        ]
        valid_bkwd_values = [
            {
                "peak": 0,
                "peak_time": 0,
                "peak_min": 0,
                "peak_min_time": 0,
                "level": 0,
                "row_num": 0,
            }
        ]
        return valid_fwd_values, valid_bkwd_values

    if (
        valid_bkwd_values[0]["peak_min_time"]
        <= valid_fwd_values[0]["peak_min_time"] - pd.Timedelta(20, "min")
        and valid_fwd_values[0]["peak_min_time"] < valid_bkwd_values[0]["peak_min_time"]
    ):
        valid_fwd_values = valid_fwd_values
        valid_bkwd_values = valid_bkwd_values

    return valid_fwd_values, valid_bkwd_values


def infer_fill_and_drain(data, shift_start: dt.datetime, shift_end: dt.datetime):
    fwd_filtered_data, fwd_mds = infer_tank_level(data.tank_volume)
    bkwd_filtered_data, bkwd_mds = infer_tank_level(data.tank_volume[::-1])

    fwd_est = []
    for i in fwd_filtered_data:
        fwd_est.append(i[0][0])
    data["filtered_vol_fwd"] = fwd_est

    bkwd_est = []
    for i in bkwd_filtered_data:
        bkwd_est.append(i[0][0])
    data["filtered_vol_bkwd"] = bkwd_est[::-1]

    data["infer_dff"] = data.filtered_vol_bkwd - data.filtered_vol_fwd
    data["fwd_mds"] = fwd_mds
    data["bkwd_mds"] = bkwd_mds[::-1]

    data = data.loc[shift_start:shift_end]
    data["row_num"] = list(range(0, len(data)))

    fwd_values = find_md_stuff(data, "fwd_mds", "row_num", "filtered_vol_fwd", -1)
    bkwd_values = find_md_stuff(data, "bkwd_mds", "row_num", "filtered_vol_bkwd")

    if len(fwd_values) == 0 or len(bkwd_values) == 0:
        fwd_values = [
            {
                "peak": 0,
                "peak_time": 0,
                "peak_min": 0,
                "peak_min_time": 0,
                "level": 0,
                "row_num": 0,
            }
        ]
        bkwd_values = [
            {
                "peak": 0,
                "peak_time": 0,
                "peak_min": 0,
                "peak_min_time": 0,
                "level": 0,
                "row_num": 0,
            }
        ]
    elif len(fwd_values) > 5 or len(bkwd_values) > 5:
        fwd_values = [
            {
                "peak": 0,
                "peak_time": 0,
                "peak_min": 0,
                "peak_min_time": 0,
                "level": 0,
                "row_num": 0,
            }
        ]
        bkwd_values = [
            {
                "peak": 0,
                "peak_time": 0,
                "peak_min": 0,
                "peak_min_time": 0,
                "level": 0,
                "row_num": 0,
            }
        ]

    valid_fwd_values, valid_bkwd_values = eliminate_false_readings(
        fwd_values, bkwd_values
    )
    return valid_fwd_values, valid_bkwd_values, data["inlet_flowrate"].sum()


def calculate_chemical_usage(valid_fwd_values, valid_bkwd_values):
    spent_vol = []
    for values in zip(valid_fwd_values, valid_bkwd_values):
        vol_diff = round(level_diff(values[0]["level"], values[1]["level"]), 2)
        spent_vol.append(vol_diff)
    chem_spent = sum(spent_vol)

    return chem_spent
