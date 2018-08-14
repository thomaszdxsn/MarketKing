"""
author: thomaszdxsn
"""
from datetime import datetime
from dataclasses import dataclass, field

from .. import DataClassAbstract, add_slots
from .._factories import factory_utcnow

__all__ = (
    'OkexSpotDepth',
    'OkexFutureDepth',
    'BinanceDepth'
)


@add_slots
@dataclass
class Depth(DataClassAbstract):
    bids: list
    asks: list
    pair: str
    server_created: datetime=None
    created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class OkexSpotDepth(Depth):
    pass


@add_slots
@dataclass
class OkexFutureDepth(Depth):
    contract_type: str='this_week'


@add_slots
@dataclass
class BinanceDepth(Depth):
    last_update_id: str=''