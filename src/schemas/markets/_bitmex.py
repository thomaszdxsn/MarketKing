"""
author: thomaszdxsn

因为bitmex有很多不一样的数据类型，所以单独建一个文件
"""
from datetime import datetime
from dataclasses import field, dataclass

from . import MarketItemBase
from .. import add_slots
from .._factories import factory_utcnow

__all__ = (
    'BitmexTrade',
    'BitmexTradeBin',
    'BitmexQuoteBin',
    'BitmexDepth',
    'BitmexSettlement'
)


@add_slots
@dataclass
class BitmexTrade(MarketItemBase):
    pair: str
    side: str
    size: int
    price: float
    tick_direction: str
    tid: str
    gross_value: int
    home_notional: float
    foreign_notional: float
    trade_time: datetime
    created: datetime=field(default_factory=factory_utcnow)

    def get_unique_indexes(self):
        return ('tid',)


@add_slots
@dataclass
class BitmexTradeBin(MarketItemBase):
    pair: str
    start_time: datetime
    open: float
    high: float
    low: float
    close: float
    trades: int
    vol: int
    vwap: float
    last_size: int
    turnover: int
    home_notional: float
    foreign_notional: float
    created: datetime = field(default_factory=factory_utcnow)

    def get_unique_indexes(self):
        return 'pair', 'start_time'


@add_slots
@dataclass
class BitmexQuoteBin(MarketItemBase):
    pair: str
    start_time: datetime
    bid_size: int
    bid_price: float
    ask_price: float
    ask_size: int
    created: datetime = field(default_factory=factory_utcnow)

    def get_unique_indexes(self):
        return 'pair', 'start_time'


@add_slots
@dataclass
class BitmexDepth(MarketItemBase):
    pair: str
    asks: list
    bids: list
    server_created: datetime
    created: datetime = field(default_factory=factory_utcnow)


@add_slots
@dataclass
class BitmexSettlement(MarketItemBase):
    pair: str
    start_time: datetime
    settlement_type: str
    settled_price: float
    option_strike_price: float
    option_underlying_price: float
    bankrupt: int
    tax_base: int
    tax_rate: float
    created: datetime = field(default_factory=factory_utcnow)

    def get_unique_indexes(self):
        return 'pair', 'start_time'