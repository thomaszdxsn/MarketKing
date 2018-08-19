"""
author: thomaszdxsn
"""
import json
from typing import Dict

import arrow
from aiohttp import WSMessage

from . import MonitorAbstract
from ..sdk.hitbtc import HitBTCWebsocket, HitBTCRest
from ..schemas.markets import (HitBTCTicker, HitBTCTrades, HitBTCKline,
                               HitBTCOrderbook, HitBTCDepth)

__all__ = (
    'HitBTCMonitor',
)

ORDERBOOK_DICT = Dict[str, HitBTCOrderbook]


class HitBTCMonitor(MonitorAbstract):
    exchange = 'hitbtc'
    _rest_sdk_class = HitBTCRest
    _ws_sdk_class = HitBTCWebsocket

    def __init__(self, *args, **kwargs):
        super(HitBTCMonitor, self).__init__(*args, **kwargs)
        self.orderbooks: ORDERBOOK_DICT=dict()

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_ticker(symbol)
            self.ws_sdk.register_depth(symbol)
            self.ws_sdk.register_trades(symbol)
            self.ws_sdk.register_kline(symbol)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)
        self.scheduler.add_job(
            self._transport_depth_snapshot,
            trigger='cron',
            second=f'*/{self._depth_interval}'
        )

    async def dispatch_ws_msg(self, msg: WSMessage):
        data = json.loads(msg.data)
        if 'method' not in data:
            return
        method = data['method']
        if 'Trades' in method:
            await self._handle_trades(data)
        elif 'Candles' in method:
            await self._handle_kline(data)
        elif 'Orderbook' in method:
            await self._handle_depth(data)
        elif method == 'ticker':
            await self._handle_ticker(data)

    async def _handle_trades(self, data: dict):
        trades = [
            HitBTCTrades(
                tid=item['id'],
                price=float(item['price']),
                amount=float(item['quantity']),
                direction=item['side'],
                trade_time=arrow.get(item['timestamp']).naive,
                pair=data['params']['symbol']
            )
            for item in data['params']['data']
        ]
        [self.transport('trades', t) for t in trades]

    async def _handle_kline(self, data: dict):
        klines = [
            HitBTCKline(
                open=float(item['open']),
                close=float(item['close']),
                low=float(item['min']),
                high=float(item['max']),
                vol=float(item['volume']),
                quote_vol=float(item['volumeQuote']),
                start_time=arrow.get(item['timestamp']).naive,
                pair=data['params']['symbol']
            )
            for item in data['params']['data']
        ]
        [self.transport('kline', k) for k in klines]

    async def _handle_ticker(self, data: dict):
        params = data['params']
        ticker = HitBTCTicker(
            ask=float(params['ask']),
            bid=float(params['bid']),
            last=float(params['last']),
            open=float(params['open']),
            low=float(params['low']),
            high=float(params['high']),
            vol=float(params['volume']),
            quote_vol=float(params['volumeQuote']),
            server_created=arrow.get(params['timestamp']).naive,
            pair=params['symbol']
        )
        self.transport('ticker', ticker)

    async def _handle_depth(self, data: dict):
        method = data['method']
        pair = data['params']['symbol']
        if method == 'snapshotOrderbook':
            orderbook = HitBTCOrderbook(pair)
            orderbook.initialize(data)
            self.orderbooks[pair] = orderbook
        else:
            orderbook = self.orderbooks[pair]
            await orderbook.update_async(data)

    async def _transport_depth_snapshot(self):
        for orderbook in self.orderbooks.values():
            snapshot = await orderbook.snapshot_async()
            self.transport('depth', snapshot)