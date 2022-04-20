# coding: utf-8
from sqlalchemy import (
    Column,
    Float,
    Integer,
    Table,
    Unicode,
)
from sqlalchemy.dialects.mssql import (
    DATETIME2,
    TINYINT,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata



t_AnalogHistory = Table(
    "AnalogHistory",
    metadata,
    Column("DateTime", DATETIME2, nullable=False),
    Column("TagName", Unicode(256), nullable=False),
    Column("Value", Float(53)),
    Column("Quality", TINYINT, nullable=False),
    Column("QualityDetail", Integer),
    Column("OPCQuality", Integer),
    Column("wwTagKey", Integer, nullable=False),
    Column("wwRowCount", Integer),
    Column("wwResolution", Integer),
    Column("wwEdgeDetection", Unicode(16)),
    Column("wwRetrievalMode", Unicode(16)),
    Column("wwTimeDeadband", Integer),
    Column("wwValueDeadband", Float(53)),
    Column("wwTimeZone", Unicode(50)),
    Column("wwVersion", Unicode(30)),
    Column("wwCycleCount", Integer),
    Column("wwTimeStampRule", Unicode(20)),
    Column("wwInterpolationType", Unicode(20)),
    Column("wwQualityRule", Unicode(20)),
    Column("wwParameters", Unicode(128)),
)

