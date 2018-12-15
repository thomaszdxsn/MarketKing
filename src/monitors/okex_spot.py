"""
author: thomaszdxsn
"""
import json
import collections
from datetime import datetime
from asyncio.locks import Lock

import arrow
from aiohttp import WSMsgType

from . import MonitorAbstract
from ..utils import decompress_okex_data
from ..sdk.okex_spot import OkexSpotRest, OkexSpotWebsocket
from ..schemas import regexes
from ..schemas.markets import (OkexSpotDepth, OkexSpotTicker,
                               OkexSpotTrades, OkexSpotKline)

__all__ = (
    'OkexSpotMonitor',
)


class OkexSpotMonitor(MonitorAbstract):
    exchange = 'okex_spot'
    _rest_sdk_class = OkexSpotRest
    _ws_sdk_class = OkexSpotWebsocket

    def __init__(self, *args, **kwargs):
        super(OkexSpotMonitor, self).__init__(*args, **kwargs)
        self._orderbooks = collections.defaultdict(dict)
        self._orderbooks_lock = Lock()
        self._orderbooks_use_snapshots = False

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_ticker(symbol)
            self.ws_sdk.register_depth(symbol)
            self.ws_sdk.register_trades(symbol)
            self.ws_sdk.register_kline(symbol)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)
        if self._orderbooks_use_snapshots:
            self.scheduler.add_job(self._transport_depth_snapshot,
                                   trigger='cron',
                                   second='*')

    async def dispatch_ws_msg(self, msg):
        json_data = decompress_okex_data(msg.data)
        data = json.loads(json_data)[0]
        channel = data['channel']
        if channel == 'addChannel':
            return
        # bch_eth 403?
        if isinstance(data['data'], dict) and data['data'].get('result', None) is False:
            return

        match_dict = regexes.OKEX_SPOT_WS_CHANS.match(channel).groupdict()
        pair = f"{match_dict['base']}_{match_dict['quote']}"
        data_type = match_dict['data_type']
        if data_type == 'ticker':
            await self._handle_ticker(data, pair)
        elif 'depth' in data_type:
            await self._handle_depth(data, pair)
        elif data_type == 'deals':
            await self._handle_trades(data, pair)
        else:
            await self._handle_kline(data, pair)

    async def _handle_ticker(self, data: dict, pair: str):
        data_dict = data['data']
        server_created = datetime.utcfromtimestamp(data_dict['timestamp']/1000)
        ticker = OkexSpotTicker(
            pair=pair,
            high=float(data_dict['high']),
            low=float(data_dict['low']),
            last=float(data_dict['last']),
            open=float(data_dict['open']),
            close=float(data_dict['close']),
            bid=float(data_dict['buy']),
            ask=float(data_dict['sell']),
            vol=float(data_dict['vol']),
            day_high=float(data_dict['dayHigh']),
            day_low=float(data_dict['dayLow']),
            server_created=server_created
        )
        self.transport('ticker', ticker)

    def __format_trade_time(self, trade_time: str) -> datetime:
        """
        '06:58:33' -> utc datetime
        """
        hour, minute, second = trade_time.split(':')
        return arrow.now().replace(
            hour=int(hour),
            minute=int(minute),
            second=int(second)
        ).to('UTC').naive

    async def _handle_trades(self, data: dict, pair: str):
        trades = [
            OkexSpotTrades(
                pair=pair,
                tid=item[0],
                price=float(item[1]),
                amount=float(item[2]),
                direction=item[4],
                trade_time=item[3]
            )
            for item in data['data']
        ]
        list(map(
            lambda x: self.transport('trades', x),
            trades
        ))

    async def _handle_kline(self, data: dict, pair: str):
        klines = [
            OkexSpotKline(
                pair=pair,
                start_time=datetime.utcfromtimestamp(int(item[0]) / 1000),
                open=item[1],
                high=item[2],
                low=item[3],
                close=item[4],
                vol=item[5]
            )
            for item in data['data']
        ]
        list(map(
            lambda x: self.transport('kline', x),
            klines
        ))

    async def _handle_depth(self, data: dict, pair: str):
        if self._orderbooks_use_snapshots:
            async with self._orderbooks_lock:
                self._orderbooks[pair].update(data)
        else:
            depth = self._format_depth(data, pair)
            self.transport('depth', depth)

    async def _transport_depth_snapshot(self):
        async with self._orderbooks_lock:
            for pair, orderbook_data in self._orderbooks.items():
                depth = self._format_depth(orderbook_data, pair)
                self.transport('depth', depth)

    def _format_depth(self, data: dict, pair: str) -> OkexSpotDepth:
        asks = [
            {
                'price': float(item[0]),
                'amount': float(item[1])
            }
            for item in reversed(data['data']['asks'])
        ]
        bids = [
            {
                'price': float(item[0]),
                'amount': float(item[1])
            }
            for item in data['data']['bids']
        ]
        server_created = datetime.utcfromtimestamp(
            data['data']['timestamp']/1000
        )
        depth = OkexSpotDepth(
            asks=asks,
            bids=bids,
            pair=pair,
            server_created=server_created
        )
        return depth
