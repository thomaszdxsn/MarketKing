"""
author: thomaszdxsn
"""
from datetime import datetime
from dataclasses import dataclass, field

from .. import DataClassAbstract, add_slots
from .._factories import factory_utcnow

__all__ = (
    'OkexSpotTicker',
    'OkexFutureTicker',
    'BinanceTicker'
)


@add_slots
@dataclass
class Ticker(DataClassAbstract):
    high: float
    low: float
    vol: float
    bid: float
    ask: float
    pair: str
    created: datetime=field(default_factory=factory_utcnow)
    server_created: datetime=None


@add_slots
@dataclass
class OkexSpotTicker(Ticker):
    day_low: float=0.0
    day_high: float=0.0
    change: float=0.0
    open: float=0.0
    close: float=0.0
    last: float=0.0


@add_slots
@dataclass
class OkexFutureTicker(Ticker):
    contract_type: str='this_week'
    limit_low: float=0.0
    limit_high: float=0.0
    hold_amount: float=0.0
    unit_amount: float=0.0
    contract_id: str=''
    last: float=0.0


@add_slots
@dataclass
class BinanceTicker(Ticker):
    event_time: datetime=None
    close: float=0.0
    open: float=0.0
    quote_vol: float=0.0
    price_change: float=0.0
    price_change_prec: float=0.0
    weighted_avg_price: float=0.0
    close_amount: float=0.0
    bbq: float=0.0              # best bid quantity
    baq: float=0.0              # best ask quantity
    open_time: datetime=None
    close_time: datetime=None
    first_trade_id: str=''
    last_trade_id: str=''
    total_trades: int=0

