"""
author: thomaszdxsn
"""
from datetime import datetime
from dataclasses import dataclass, field

from .. import DataClassAbstract, add_slots
from .._factories import factory_utcnow

__all__ = (
    'OkexSpotTrades',
    'OkexFutureTrades',
    'BinanceTrades'
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


@add_slots
@dataclass
class OkexFutureTrades(Trades):
    contract_type: str='this_week'


@add_slots
@dataclass
class BinanceTrades(Trades):
    event_time: datetime=None
    buyer_order_id: str=''
    seller_order_id: str=''
    is_buyer_maker: bool=False