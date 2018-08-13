"""
author: thomaszdxsn
"""
from datetime import datetime
from dataclasses import dataclass, field

from .. import DataClassAbstract, add_slots
from .._factories import factory_utcnow

__all__ = (
    'OkexSpotTicker',
    'OkexFutureTicker'
)


@add_slots
@dataclass
class Ticker(DataClassAbstract):
    high: float
    low: float
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
    day_low: float=0.0
    day_high: float=0.0
    change: float=0.0
    open: float=0.0
    close: float=0.0


@add_slots
@dataclass
class OkexFutureTicker(Ticker):
    contract_type: str='this_week'
    limit_low: float=0.0
    limit_high: float=0.0
    hold_amount: float=0.0
    unit_amount: float=0.0
    contract_id: str=''
