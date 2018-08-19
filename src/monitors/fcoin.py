"""
author: thomaszdxsn
"""
import json
from datetime import datetime

from aiohttp import WSMessage

from . import MonitorAbstract
from ..utils import chunk
from ..sdk.fcoin import FcoinWebsocket, FcoinRest
from ..schemas.regexes import FCOIN_WS_CHANS
from ..schemas.markets import (FcoinTicker, FcoinDepth,
                               FcoinKline, FcoinTrades)

__all__ = (
    'FcoinMonitor',
)


class FcoinMonitor(MonitorAbstract):
    exchange = 'fcoin'
    _ws_sdk_class = FcoinWebsocket
    _rest_sdk_class = FcoinRest

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_depth(symbol)
            self.ws_sdk.register_trades(symbol)
            self.ws_sdk.register_ticker(symbol)
            self.ws_sdk.register_kline(symbol)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)

    async def dispatch_ws_msg(self, msg: WSMessage):
        data = json.loads(msg.data)
        type_field = data['type']
        if type_field in ('hello', 'topics'):
            return
        match_dict = FCOIN_WS_CHANS.match(type_field).groupdict()
        data_type = match_dict['data_type']
        pair = match_dict['symbol']

        if data_type == 'ticker':
            await self._handle_ticker(data, pair)
        elif data_type == 'depth':
            await self._handle_depth(data, pair)
        elif data_type == 'candle':
            await self._handle_kline(data, pair)
        elif data_type == 'trade':
            await self._handle_trades(data, pair)

    async def _handle_ticker(self, data: dict, pair: str):
        tick_data = data['ticker']
        ticker = FcoinTicker(
            pair=pair,
            last=tick_data[0],
            last_size=tick_data[1],
            bid=tick_data[2],
            bid_size=tick_data[3],
            ask=tick_data[4],
            ask_size=tick_data[5],
            open=tick_data[6],
            high=tick_data[7],
            low=tick_data[8],
            base_vol=tick_data[9],
            quote_vol=tick_data[10]
        )
        self.transport('ticker', ticker)

    async def _handle_depth(self, data: dict, pair: str):
        bids = [
            {
                'price': item[0],
                'amount': item[1]
            }
            for item in chunk(data['bids'], 2)
        ]
        asks = [
            {
                'price': item[0],
                'amount': item[1]
            }
            for item in chunk(data['asks'], 2)
        ]
        depth = FcoinDepth(
            asks=asks,
            bids=bids,
            pair=pair,
            server_created=datetime.utcfromtimestamp(data['ts'] / 1000)
        )
        self.transport('depth', depth)

    async def _handle_kline(self, data: dict, pair: str):
        kline = FcoinKline(
            pair=pair,
            open=data['open'],
            close=data['close'],
            high=data['high'],
            quote_vol=data['quote_vol'],
            start_time=datetime.utcfromtimestamp(data['id']),
            count=data['count'],
            low=data['low'],
            vol=data['base_vol']
        )
        self.transport('kline', kline)

    async def _handle_trades(self, data: dict, pair: str):
        trade = FcoinTrades(
            pair=pair,
            trade_time=datetime.utcfromtimestamp(data['ts'] / 1000),
            amount=data['amount'],
            price=data['price'],
            direction=data['side'],
            tid=data['id']
        )
        self.transport('trades', trade)

