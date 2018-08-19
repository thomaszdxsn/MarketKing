"""
Author: thomaszdxsn
"""
from datetime import datetime

from aiohttp import WSMessage

from . import MonitorAbstract
from ..sdk.huobi import HuobiRest, HuobiWebsocket
from ..schemas.regexes import HUOBI_WS_CHANS
from ..schemas.markets import (HuobiDepth, HuobiTicker, HuobiKline,
                               HuobiTrades)

__all__ = (
    'HuobiMonitor',
)


class HuobiMonitor(MonitorAbstract):
    exchange = 'huobi'
    _ws_sdk_class = HuobiWebsocket
    _rest_sdk_class = HuobiRest

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_depth(symbol)
            self.ws_sdk.register_trades(symbol)
            self.ws_sdk.register_kline(symbol)
            self.ws_sdk.register_ticker(symbol)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)

    async def dispatch_ws_msg(self, msg: WSMessage):
        data = await self.ws_sdk.handle_ws_ping(msg)
        if not data.get('ch'):
            if 'ping' not in data:
                self._log_sub_msg(data)
            return
        self._log_msg(data)
        match_dict = HUOBI_WS_CHANS.match(data['ch']).groupdict()
        pair, data_type = match_dict['symbol'], match_dict['data_type']
        if data_type == 'detail':
            await self._handle_ticker(data, pair)
        elif data_type == 'kline':
            await self._handle_kline(data, pair)
        elif data_type == 'trade':
            await self._handle_trades(data, pair)
        else:
            await self._handle_depth(data, pair)

    async def _handle_depth(self, data: dict, pair: str, size: int=20):
        tick = data['tick']
        asks = [
            {
                'price': item[0],
                'amount': item[1]
            }
            for item in tick['asks'][:size]
        ]
        bids = [
            {
                'price': item[0],
                'amount': item[1]
            }
            for item in tick['bids'][:size]
        ]
        depth = HuobiDepth(
            pair=pair,
            server_created=datetime.utcfromtimestamp(tick['ts'] / 1000),
            event_time=datetime.utcfromtimestamp(data['ts'] / 1000),
            version=tick['version'],
            bids=bids,
            asks=asks
        )
        self.transport('depth', depth)

    async def _handle_ticker(self, data: dict, pair: str):
        tick = data['tick']
        ticker = HuobiTicker(
            pair=pair,
            server_created=datetime.utcfromtimestamp(data['ts'] / 1000),
            amount=tick['amount'],
            open=tick['open'],
            close=tick['close'],
            high=tick['high'],
            low=tick['low'],
            id=tick['id'],
            count=tick['count'],
            vol=tick['vol']
        )
        self.transport('ticker', ticker)

    async def _handle_kline(self, data: dict, pair: str):
        tick = data['tick']
        kline = HuobiKline(
            pair=pair,
            start_time=datetime.utcfromtimestamp(tick['id']),
            event_time=datetime.utcfromtimestamp(data['ts'] / 1000),
            open=tick['open'],
            close=tick['close'],
            low=tick['low'],
            high=tick['high'],
            amount=tick['amount'],
            vol=tick['vol'],
            count=tick['count']
        )
        self.transport('kline', kline)

    async def _handle_trades(self, data: dict, pair: str):
        tick = data['tick']
        trades = [
            HuobiTrades(
                pair=pair,
                event_time=datetime.utcfromtimestamp(data['ts'] / 1000),
                id=tick['id'],
                amount=item['amount'],
                trade_time=datetime.utcfromtimestamp(item['ts'] / 1000),
                tid=str(item['id']),
                price=item['price'],
                direction=item['direction']
            )
            for item in tick['data']
        ]
        list(map(
            lambda x: self.transport('trades', x),
            trades
        ))
