"""
author: thomaszdxsn
"""
import json
from typing import Dict

import arrow
from aiohttp import WSMessage

from . import MonitorAbstract
from ..sdk.poloniex import PoloniexWebsocket, PoloniexRest, SYMBOLS_MAP
from ..schemas.markets import (PoloniexOrderbook, Orderbook, PoloniexTrades,
                               PoloniexTicker, PoloniexDepth)

__all__ = (
    'PoloniexMonitor',
)

ORDERBOOKS_DICT = Dict[str, Orderbook]


class PoloniexMonitor(MonitorAbstract):
    exchange = 'poloniex'
    _ws_sdk_class = PoloniexWebsocket
    _rest_sdk_class = PoloniexRest

    def __init__(self, *args, **kwargs):
        super(PoloniexMonitor, self).__init__(*args, **kwargs)
        self.symbols_set = set(self.symbols)    # for O(1) lookup
        self._orderbooks: ORDERBOOKS_DICT = dict()

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_depth(symbol)
        self.ws_sdk.register_ticker()
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)
        self.scheduler.add_job(
            self._transport_depth_snapshots,
            trigger='cron',
            second=f'*/{self._depth_interval}'
        )

    async def dispatch_ws_msg(self, msg: WSMessage):
        data = json.loads(msg.data)
        code = data[0]
        if code == 1010:
            # heartbeat
            return
        elif code == 1002:
            # ticker
            await self._handle_ticker(data)
        else:
            await self._handle_orderbook_data(data)

    async def _handle_orderbook_data(self, data: list):
        pair = SYMBOLS_MAP[data[0]]
        condition_node = data[2][0][1]
        is_snapshot = isinstance(condition_node, dict)
        if is_snapshot:
            orderbook = PoloniexOrderbook(pair)
            orderbook.initialize(condition_node['orderBook'])
            self._orderbooks[pair] = orderbook
            return
        # handle update
        for item in data[2]:
            data_type = item[0]
            if data_type == 'o':
                await self._handle_depth(item, pair)
            else:
                await self._handle_trades(item, pair)

    async def _handle_depth(self, item: list, pair: str):
        orderbook = self._orderbooks[pair]
        await orderbook.update_async(item)

    async def _transport_depth_snapshots(self):
        for orderbook in self._orderbooks.values():
            depth: PoloniexDepth = await orderbook.snapshot_async()
            self.transport('depth', depth)

    async def _handle_trades(self, item: list, pair: str):
        trade = PoloniexTrades(
            pair=pair,
            tid=item[1],
            direction='buy' if item[2] == 1 else 'sell',
            amount=float(item[3]),
            price=float(item[4]),
            trade_time=arrow.get(item[5]).naive
        )
        self.transport('trades', trade)

    async def _handle_ticker(self, data: dict):
        if len(data) < 3:
            # subscribe info
            return
        item = data[2]
        pair = SYMBOLS_MAP.get(item[0], '')
        if pair not in self.symbols_set:
            # not collected symbols
            return
        ticker = PoloniexTicker(
            pair=pair,
            last=float(item[1]),
            ask=float(item[2]),
            bid=float(item[3]),
            change_perc=float(item[4]),
            base_vol=float(item[5]),
            quote_vol=float(item[6]),
            is_frozen=bool(item[7]),
            high=float(item[8]),
            low=float(item[9])
        )
        self.transport('ticker', ticker)






