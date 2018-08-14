"""
author: thomaszdxsn
"""
from datetime import datetime
from dataclasses import dataclass, field

from .. import DataClassAbstract, add_slots
from .._factories import factory_utcnow

__all__ = (
    'OkexSpotKline',
    'OkexFutureKline',
    'BinanceKline',
    'HuobiKline'
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
class OkexFutureKline(Kline):
    contract_type: str='this_week'
    sheet_vol: float=0.0
    token_vol: float=0.0



@add_slots
@dataclass
class BinanceKline(Kline):
    event_time: datetime=None
    first_trade_id: str=''
    last_trade_id: str=''
    total_trades: int=0
    is_completed: bool=False
    quote_vol: float=0.0
    taker_base_vol: float=0.0
    taker_quote_vol: float=0.0


@add_slots
@dataclass
class HuobiKline(Kline):
    event_time: datetime=None
    amount: float=0
    count: int=0