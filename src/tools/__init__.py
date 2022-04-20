# -*- coding: utf-8 -*-
"""A set of modules used to pull data for division locations and units"""

__author__ = "User 1"
__license__ = "proprietary"
__copyright__ = "************"


__version__ = "1.0.16"


__maintainer__ = "User 1"

import os

from dotenv import load_dotenv

load_dotenv()
if os.getenv("DEBUG") is not None:
    print("DEBUG: " + os.getenv("DEBUG"))
else:
    print(os.getenv("DEBUG"))
