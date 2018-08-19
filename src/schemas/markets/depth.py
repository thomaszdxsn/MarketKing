"""
author: thomaszdxsn
"""
from datetime import datetime
from dataclasses import dataclass, field

from . import MarketItemBase
from .. import add_slots
from .._factories import factory_utcnow

__all__ = (
    'OkexSpotDepth',
    'OkexFutureDepth',
    'BinanceDepth',
    'HuobiDepth',
    'BitfinexFundingDepth',
    'BitfinexTradeDepth',
    'BitflyerDepth',
    'HitBTCDepth',
    'PoloniexDepth'
)


@add_slots
@dataclass
class Depth(MarketItemBase):
    bids: list
    asks: list
    pair: str
    created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class OkexSpotDepth(Depth):
    server_created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class OkexFutureDepth(Depth):
    contract_type: str='this_week'
    server_created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class BinanceDepth(Depth):
    last_update_id: str=''


@add_slots
@dataclass
class HuobiDepth(Depth):
    event_time: datetime=field(default_factory=factory_utcnow)
    server_created: datetime=field(default_factory=factory_utcnow)
    version: int=0


@add_slots
@dataclass
class BitfinexTradeDepth(Depth):
    pass


@add_slots
@dataclass
class BitfinexFundingDepth(Depth):
    pass


@add_slots
@dataclass
class BitflyerDepth(MarketItemBase):
    pair: str
    asks: list
    bids: list
    mid_price: float
    created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class HitBTCDepth(Depth):
    pass


@add_slots
@dataclass
class PoloniexDepth(Depth):
    pass