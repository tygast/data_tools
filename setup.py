# -*- coding: utf-8 -*-
"""Run Setup Script to build data_tools module"""
import re

from setuptools import setup

with open("src/tools/__init__.py", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    version=version,
    description=(
        "A set of modules used to pull data for"
        "division location and unit operations"
    ),
)