"""
author: thomaszdxsn
"""
from datetime import datetime
from dataclasses import dataclass, field

from .. import DataClassAbstract, add_slots
from .._factories import factory_utcnow

__all__ = (
    'OkexSpotKline',
    'OkexFutureKline'
)


@add_slots
@dataclass
class Kline(DataClassAbstract):
    pair: str
    start_time: datetime
    open: float
    close: float
    high: float
    low: float
    vol: float
    created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class OkexSpotKline(Kline):
    pass


@add_slots
@dataclass
class OkexFutureKline(DataClassAbstract):
    pair: str
    contract_type: str
    start_time: datetime
    open: float
    close: float
    high: float
    low: float
    sheet_vol: float
    token_vol: float
    created: datetime = field(default_factory=factory_utcnow)