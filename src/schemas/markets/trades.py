"""
author: thomaszdxsn
"""
from datetime import datetime
from dataclasses import dataclass, field

from .. import DataClassAbstract, add_slots
from .._factories import factory_utcnow

__all__ = (
    'OkexSpotTrades',
)


@add_slots
@dataclass
class Trades(DataClassAbstract):
    pair: str
    tid: str
    price: float
    amount: float
    direction: str
    trade_time: datetime
    created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class OkexSpotTrades(Trades):
    pass