# -*- coding: utf-8 -*-
def calculate_product_summary_stats(data):
    inlet_avg = data.inlet_flowrate.mean()
    if data.cumulative_inlet.iloc[-1] > 0:
        product_avg_gpm = (
            (
                data.cumulative_liquid_product_flowrate.iloc[-1]
                + data.product_tank_volume.iloc[-1]
                - data.product_tank_volume.iloc[0]
            )
            / data.cumulative_inlet.iloc[-1]
        ) / 1000
    else:
        product_avg_gpm = 0
    product_gal = data.cumulative_product.iloc[-1] / 42
    return inlet_avg, product_avg_gpm, product_gal


def calculate_flow_summary_stats(data):
    fuel_gas_avg = data.fuel_flowrate.mean()
    try:
        inlet_avg = data.inlet_flowrate.mean()
    except AttributeError:
        inlet_avg = 0
    try:
        discharge_avg = data.discharge_flowrate.mean()
    except AttributeError:
        discharge_avg = 0
    return inlet_avg, fuel_gas_avg, discharge_avg


def calculate_pressure_summary_stats(data):
    inlet_pressure_avg = data.mean()
    return inlet_pressure_avg
