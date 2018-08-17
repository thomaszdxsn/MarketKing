"""
author: thomaszdxsn
"""
from abc import ABC, abstractmethod
from asyncio import locks
from datetime import datetime
from dataclasses import dataclass, field
from typing import List

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
    'BitfinexFundingOrderbook',
    'BitfinexTradeOrderbook',
    'BitflyerDepth'
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


class Orderbook(ABC):

    def __init__(self, pair: str):
        self._bids = dict()
        self._asks = dict()
        self._async_lock = locks.Lock()
        self._pair = pair

    def initialize(self, data_list: List[list]):
        """通过snapshot初始化"""
        for item in data_list:
            self.update(item)

    @abstractmethod
    def update(self, item: list):
        """通过update更新orderbook"""

    async def update_async(self, item: list):
        async with self._async_lock:
            self.update(item)

    def snapshot(self) -> Depth:
        raise NotImplementedError()

    async def snapshot_async(self) -> Depth:
        async with self._async_lock:
            return self.snapshot()


class BitfinexTradeOrderbook(Orderbook):
    """
    [6094, 1, 0.210617]
    (price, count, amount)
    count: Number of orders at that price level
    amount: Total amount available at that price level.
            Trading: if AMOUNT > 0 then bid else ask;
    """

    def update(self, item: list):
        price, count, amount = item
        book = self._bids if amount > 0 else self._asks
        if count > 0:
            book[price] = {
                'count': count,
                'amount': amount,
            }
        else:
            book.pop(price, None)

    def snapshot(self) -> BitfinexTradeDepth:
        bids = [
            {
                'price': price,
                'count': info['count'],
                'amount': info['amount']
            }
            for price, info in
            sorted(self._bids.items(), key=lambda x: -x[0])
        ]
        asks = [
            {
                'price': price,
                'count': info['count'],
                'amount': info['amount']
            }
            for price, info in
            sorted(self._asks.items(), key=lambda x: x[0])
        ]
        return BitfinexTradeDepth(
            pair=self._pair,
            asks=asks,
            bids=bids
        )


class BitfinexFundingOrderbook(Orderbook):
    """
    [0.00011, 30, 5, -29300]
    (rate, period, count, amount)

    rate: rate level
    period: period level
    count: Number of orders at that price level
    amount: Total amount available at that price level.
            Funding: if AMOUNT < 0 then bid else ask;
    """

    def update(self, item: list):
        rate, period, count, amount = item
        book = self._bids if amount < 0 else self._asks
        if count > 0:
            book[rate] = {
                'count': count,
                'amount': amount,
                'period': period
            }
        else:
            book.pop(rate, None)

    def snapshot(self) -> BitfinexFundingDepth:
        bids = [
            {
                'rate': rate,
                'count': info['count'],
                'amount': info['amount'],
                'period': info['period']
            }
            for rate, info in
            sorted(self._bids.items(), key=lambda x: -x[0])
        ]
        asks = [
            {
                'rate': rate,
                'count': info['count'],
                'amount': info['amount'],
                'period': info['period']
            }
            for rate, info in
            sorted(self._asks.items(), key=lambda x: x[0])
        ]
        return BitfinexFundingDepth(
            pair=self._pair,
            asks=asks,
            bids=bids
        )


@add_slots
@dataclass
class BitflyerDepth(MarketItemBase):
    pair: str
    asks: list
    bids: list
    mid_price: float
    created: datetime=field(default_factory=factory_utcnow)