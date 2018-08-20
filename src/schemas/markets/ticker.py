"""
author: thomaszdxsn
"""
from datetime import datetime
from dataclasses import dataclass, field

from . import MarketItemBase
from .. import add_slots
from .._factories import factory_utcnow

__all__ = (
    'OkexSpotTicker',
    'OkexFutureTicker',
    'BinanceTicker',
    'HuobiTicker',
    'BitfinexFundingTicker',
    'BitfinexTradeTicker',
    'BitFlyerTicker',
    'HitBTCTicker',
    'PoloniexTicker',
    'FcoinTicker',
    'CointigerTicker',
    'BithumbTicker',
    'ZBTicker',
)


@add_slots
@dataclass
class Ticker(MarketItemBase):
    high: float
    low: float
    vol: float
    pair: str
    created: datetime=field(default_factory=factory_utcnow)
    server_created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class OkexSpotTicker(Ticker):
    day_low: float=0.0
    day_high: float=0.0
    change: float=0.0
    open: float=0.0
    close: float=0.0
    last: float=0.0
    bid: float=0.0
    ask: float=0.0


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
    bid: float=0.0
    ask: float=0.0


@add_slots
@dataclass
class BinanceTicker(Ticker):
    close: float=0.0
    open: float=0.0
    quote_vol: float=0.0
    price_change: float=0.0
    price_change_prec: float=0.0
    weighted_avg_price: float=0.0
    close_amount: float=0.0
    bid_amount: float=0.0              # best bid quantity
    ask_amount: float=0.0              # best ask quantity
    open_time: datetime=None
    close_time: datetime=None
    first_trade_id: str=''
    last_trade_id: str=''
    total_trades: int=0
    bid: float=0.0
    ask: float=0.0


@add_slots
@dataclass
class HuobiTicker(Ticker):
    open: float=0.0
    close: float=0.0
    amount: float=0.0
    id: int=0
    count: float=0.0


@add_slots
@dataclass
class BitfinexTradeTicker(MarketItemBase):
    pair: str
    bid: float
    bid_size: float
    ask: float
    ask_size: float
    daily_change: float
    daily_change_prec: float
    last: float
    vol: float
    high: float
    low: float
    created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class BitfinexFundingTicker(MarketItemBase):
    pair: str
    frr: float
    bid: float
    bid_period: float
    bid_size: float
    ask: float
    ask_period: float
    ask_size: float
    daily_change: float
    daily_change_prec: float
    last: float
    vol: float
    high: float
    low: float
    created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class BitFlyerTicker(MarketItemBase):
    pair: str
    tick_id: int
    best_bid: float
    best_ask: float
    best_bid_size: float
    best_ask_size: float
    total_bid_depth: float
    total_ask_depth: float
    ltp: float
    volume: float
    volume_by_product: float
    server_created: datetime
    created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class HitBTCTicker(Ticker):
    ask: float=0.0
    bid: float=0.0
    last: float=0.0
    open: float=0.0
    quote_vol: float=0.0
    server_created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class PoloniexTicker(MarketItemBase):
    last: float
    change_perc: float
    high: float
    low: float
    pair: str
    base_vol: float
    quote_vol: float
    is_frozen: bool
    ask: float
    bid: float
    created: datetime=field(default_factory=factory_utcnow)
    server_created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class FcoinTicker(MarketItemBase):
    pair: str
    last: float
    last_size: float
    bid: float
    bid_size: float
    ask: float
    ask_size: float
    open: float
    high: float
    low: float
    base_vol: float
    quote_vol: float
    created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class CointigerTicker(Ticker):
    amount: float=0.0
    rose: float=0.0
    close: float=0.0
    open: float=0.0
    server_created: datetime=field(default_factory=factory_utcnow)
    
    
@add_slots
@dataclass
class BithumbTicker(MarketItemBase):
    pair: str
    low: float
    high: float
    open: float
    close: float
    avg_price: float
    units_traded: float
    vol_1day: float
    vol_7day: float
    ask: float
    bid: float
    change: float
    change_perc: float
    server_created: datetime
    created: datetime = field(default_factory=factory_utcnow)


@add_slots
@dataclass
class ZBTicker(Ticker):
    ask: float=0.0
    bid: float=0.0
    last: float=0.0