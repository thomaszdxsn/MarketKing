"""
author: thomaszdxsn
"""
from abc import ABC, abstractmethod
from asyncio import locks
from typing import List

from dynaconf import settings

from .depth import (Depth, BitfinexTradeDepth, BitfinexFundingDepth,
                    HitBTCDepth, PoloniexDepth)

__all__ = (
    'BitfinexTradeOrderbook',
    'BitfinexFundingOrderbook',
    'Orderbook',
    'HitBTCOrderbook',
    'PoloniexOrderbook'
)

ORDERBOOK_LEVEL = settings.as_int('ORDERBOOK_LEVEL')


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
            sorted(self._bids.items(), key=lambda x: -x[0])[:ORDERBOOK_LEVEL]
        ]
        asks = [
            {
                'price': price,
                'count': info['count'],
                'amount': info['amount']
            }
            for price, info in
            sorted(self._asks.items(), key=lambda x: x[0])[:ORDERBOOK_LEVEL]
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
            sorted(self._bids.items(), key=lambda x: -x[0])[:ORDERBOOK_LEVEL]
        ]
        asks = [
            {
                'rate': rate,
                'count': info['count'],
                'amount': info['amount'],
                'period': info['period']
            }
            for rate, info in
            sorted(self._asks.items(), key=lambda x: x[0])[:ORDERBOOK_LEVEL]
        ]
        return BitfinexFundingDepth(
            pair=self._pair,
            asks=asks,
            bids=bids
        )


class HitBTCOrderbook(Orderbook):
    """
    doc: https://api.hitbtc.com/?python#subscribe-to-orderbook
    """

    def initialize(self, data: dict):
        params = data['params']
        for item in params['ask']:
            price, size = item['price'], item['size']
            self._asks[price] = size
        for item in params['bid']:
            price, size = item['price'], item['size']
            self._bids[price] = size

    def update(self, data: dict):
        params = data['params']
        for item in params['ask']:
            price, size = item['price'], item['size']
            if float(item['size']) == 0:
                self._asks.pop(price)
            else:
                self._asks[price] = size
        for item in params['bid']:
            price, size = item['price'], item['size']
            if float(item['size']) == 0:
                self._bids.pop(price)
            else:
                self._bids[price] = size

    def snapshot(self):
        asks = [
            {
                'price': float(price),
                'amount': float(amount)
            }
            for price, amount in sorted(
                self._asks.items(),
                key=lambda x: float(x[0])
            )[:ORDERBOOK_LEVEL]
        ]
        bids = [
            {
                'price': float(price),
                'amount': float(amount)
            }
            for price, amount in sorted(
                self._bids.items(),
                key=lambda x: -float(x[0])
            )[:ORDERBOOK_LEVEL]
        ]
        return HitBTCDepth(
            pair=self._pair,
            asks=asks,
            bids=bids
        )


class PoloniexOrderbook(Orderbook):

    def initialize(self, data_list:List[dict]):
        """
        "orderBook": [
          {
            "<lowest ask price>": "<lowest ask size>",
            "<next ask price>": "<next ask size>",
            …
          },
          {
            "<highest bid price>": "<highest bid size>",
            "<next bid price>": "<next bid size>",
            …
          }
        """
        self._asks = data_list[0]
        self._bids = data_list[1]

    def update(self, item: list):
        """
        ["o", 1, "0.00001823", "5534.6474"]
        ["o", <1 for buy 0 for sell>, "<price>", "<size>"]
        """
        side, price, size = item[1:]
        book = self._bids if side == 1 else self._asks
        if float(size) == 0:
            # remove
            book.pop(price)
        else:
            # update
            book[price] = size

    def snapshot(self) -> PoloniexDepth:
        asks = [
            {
                'price': float(price),
                'amount': float(amount)
            }
            for price, amount in
            sorted(
                self._asks.items(), key=lambda x: float(x[0])
            )[:ORDERBOOK_LEVEL]
        ]
        bids = [
            {
                'price': float(price),
                'amount': float(amount)
            }
            for price, amount in
            sorted(
                self._bids.items(), key=lambda x: -float(x[0])
            )[:ORDERBOOK_LEVEL]
        ]
        return PoloniexDepth(
            asks=asks,
            bids=bids,
            pair=self._pair
        )



