"""
author: thomaszdxsn
"""
from datetime import datetime
from dataclasses import dataclass, field

from .. import DataClassAbstract, add_slots
from .._factories import factory_utcnow

__all__ = (
    'OkexSpotTicker',
)


@add_slots
@dataclass
class Ticker(DataClassAbstract):
    high: float
    low: float
    open: float
    close: float
    last: float
    vol: float
    bid: float
    ask: float
    pair: str
    received: datetime=field(default_factory=factory_utcnow)
    created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class OkexSpotTicker(Ticker):
    dayLow: float = 0.0
    dayHigh: float = 0.0
    change: float = 0.0
    created: datetime = field(default_factory=factory_utcnow)