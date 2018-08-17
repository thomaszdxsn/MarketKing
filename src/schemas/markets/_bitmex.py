"""
author: thomaszdxsn

因为bitmex有很多不一样的数据类型，所以单独建一个文件
"""
from datetime import datetime
from dataclasses import field, dataclass
from typing import Union

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


@add_slots
@dataclass
class BitmexInstrument(MarketItemBase):
    pair: str
    server_created: datetime
    root_symbol: str
    state: str
    typ: str
    listing: datetime
    front: datetime
    expiry: Union[datetime, None]
    settle: Union[datetime, None]
    relist_interval: Union[str, None]
    inverse_leg: str
    sell_leg: str
    buy_leg: str
    option_strike_pcnt: float
    option_strike_round: float
    option_multiplier: float
    position_currency: str
    underlying: str
    quote_currency: str
    underlying_symbol: str
    reference: str
    reference_symbol: str
    calc_interval: Union[str, None]
    publish_interval: Union[str, None]
    publish_time: Union[str, None]
    max_order_qty: int
    max_price: float
    lot_size: int
    tick_size: float
    multiplier: float
    settle_currency: str
    underlying_to_position_multiplier: int
    quote_to_settle_multiplier: int
    is_quanto: bool
    is_inverse: bool
    init_margin: float
    maint_margin: float
    risk_limit: int
    risk_step: int
    limit: float
    capped: bool
    taxed: bool
    deleverage: bool
    maker_fee: float
    taker_fee: float
    settlement_fee: float
    insurance_fee: float
    funding_base_symbol: str
    funding_quote_symbol: str
    funding_premium_symbol: str
    funding_timestamp: datetime
    funding_interval: Union[str, None]
    funding_rate: float
    indicative_funding_rate: float
    rebalance_timestamp: datetime
    rebalance_interval: Union[str, None]

