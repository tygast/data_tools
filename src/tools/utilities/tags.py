# -*- coding: utf-8 -*-
from pathlib import Path

import toml

config_folder = Path(__file__).resolve().parents[1] / "configs"
config_file = config_folder / "config.toml"

with config_file.open() as f:
    configs = toml.load(f)

TAGS = configs.items()


class GetTags:
    def __init__(self):
        self.configs = configs

    def name(self, location):
        return self.configs[location]["name"]

    def connection(self, location):
        return self.configs[location]["connection_args"][0]

    def connection_type(self, location):
        return self.configs[location]["connection_args"][0]["type"]

    def designation(self, location):
        return self.configs[location]["location"][0]["designation"]

    def inlet_flowrate(self, location):
        return self.configs[location]["inlet"][0]["tags"]

    def pipeline_pressure(self, location):
        return self.configs[location]["inlet_pressure"][0]["tags"]

    def inlet_names(self, location):
        return self.configs[location]["inlet_pressure"][0]["name"]

    def discharge_flowrate(self, location):
        return self.configs[location]["discharge_flowrate"][0]["tags"]

    def liquid_product_flowrate(self, location):
        return self.configs[location]["liquid_product_flowrate"][0]["tags"]

    def product_tank_volume(self, location):
        return self.configs[location]["product_tank_vol"][0]["tags"]

    def trucked(self, location):
        return self.configs[location]["trucked"]

    def fuel(self, location):
        return self.configs[location]["fuel_flowrate"][0]["name"]

    def fuel_flowrate(self, location):
        return self.configs[location]["fuel_flowrate"][0]["tags"]

    def fuel_measurement(self, location):
        return self.configs[location]["fuel_flowrate"][0]["usage_function"]

    def chemical_a(self, location):
        return self.configs[location]["chemical_a"][0]["name"]

    def chemical_a_volume(self, location):
        return self.configs[location]["chemical_a"][0]["tags"]

    def chemical_a_measurement(self, location):
        return self.configs[location]["chemical_a"][0]["usage_function"]

    def chemical_b(self, location):
        return self.configs[location]["chemical_b"][0]["name"]

    def chemical_b_volume(self, location):
        return self.configs[location]["chemical_b"][0]["tags"]

    def chemical_b_measurement(self, location):
        return self.configs[location]["chemical_b"][0]["usage_function"]

    def chemical_c(self, location):
        return self.configs[location]["chemical_c"][0]["name"]

    def chemical_c_volume(self, location):
        return self.configs[location]["chemical_c"][0]["tags"]

    def chemical_c_measurement(self, location):
        return self.configs[location]["chemical_c"][0]["usage_function"]

    def chemical_d(self, location):
        return self.configs[location]["chemical_d"][0]["name"]

    def chemical_d_volume(self, location):
        return self.configs[location]["chemical_d"][0]["tags"]

    def chemical_d_measurement(self, location):
        return self.configs[location]["chemical_d"][0]["usage_function"]

    def chemical_e(self, location):
        return self.configs[location]["chemical_e"][0]["name"]

    def chemical_e_volume(self, location):
        return self.configs[location]["chemical_e"][0]["tags"]

    def chemical_e_measurement(self, location):
        return self.configs[location]["chemical_e"][0]["usage_function"]
