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
    'BinanceTrades',
    'HuobiTrades',
    'BitfinexFundingTrades',
    'BitfinexTradeTrades',
    'BitflyerTrades'
)


@add_slots
@dataclass
class Trades(DataClassAbstract):
    pair: str
    tid: str
    price: float
    amount: float
    trade_time: datetime
    created: datetime=field(default_factory=factory_utcnow)


@add_slots
@dataclass
class OkexSpotTrades(Trades):
    direction: str=''


@add_slots
@dataclass
class OkexFutureTrades(Trades):
    direction: str=''
    contract_type: str='this_week'


@add_slots
@dataclass
class BinanceTrades(Trades):
    event_time: datetime=None
    buyer_order_id: str=''
    seller_order_id: str=''
    is_buyer_maker: bool=False


@add_slots
@dataclass
class HuobiTrades(Trades):
    direction: str = ''
    event_time: datetime=None
    id: int=0


@add_slots
@dataclass
class BitfinexTradeTrades(Trades):
    type: str=''        # te|tu


@add_slots
@dataclass
class BitfinexFundingTrades(DataClassAbstract):
    pair: str
    type: str           # fte|ftu
    tid: str
    rate: float
    amount: float
    period: float
    trade_time: datetime
    created: datetime = field(default_factory=factory_utcnow)


@add_slots
@dataclass
class BitflyerTrades(DataClassAbstract):
    product_code: str
    tid: str
    side: str
    price: float
    size: float
    trade_time: datetime
    buy_child_order_acceptance_id: str
    sell_child_order_acceptance_id: str

