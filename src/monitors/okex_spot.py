"""
author: thomaszdxsn
"""
import json
from datetime import datetime

import arrow
from aiohttp import WSMsgType

from . import MonitorAbstract
from ..sdk.okex_spot import OkexSpotRest, OkexSpotWebsocket
from ..schemas import regexes
from ..schemas.markets import (OkexSpotDepth, OkexSpotTicker,
                               OkexSpotTrades, OkexSpotKline)

__all__ = (
    'OkexSpotMonitor',
)


class OkexSpotMonitor(MonitorAbstract):
    _rest_sdk_class = OkexSpotRest
    _ws_sdk_class = OkexSpotWebsocket

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_ticker(symbol)
            self.ws_sdk.register_depth(symbol)
            self.ws_sdk.register_trades(symbol)
            self.ws_sdk.register_kline(symbol)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)

    def dispatch_ws_msg(self, msg):
        if msg.type != WSMsgType.TEXT:
            return
        data = json.loads(msg.data)[0]
        channel = data['channel']
        if channel == 'addChannel':
            return

        match_dict = regexes.OKEX_SPOT_WS_CHANS.match(channel).groupdict()
        pair = f"{match_dict['base']}_{match_dict['quote']}"
        data_type = match_dict['data_type']
        if data_type == 'ticker':
            self._handle_ticker(data, pair)
        elif 'depth' in data_type:
            self._handle_depth(data, pair)
        elif data_type == 'deals':
            self._handle_trades(data, pair)
        else:
            self._handle_kline(data, pair)

    def _handle_ticker(self, data: dict, pair: str):
        data_dict = data['data']
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
            dayHigh=float(data_dict['dayHigh']),
            dayLow=float(data_dict['dayLow']),
            received=datetime.utcfromtimestamp(data_dict['timestamp'] / 1000)
        )

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

    def _handle_trades(self, data: dict, pair: str):
        trades = [
            OkexSpotTrades(
                pair=pair,
                tid=item[0],
                price=float(item[1]),
                amount=float(item[2]),
                direction=item[4],
                trade_time=self.__format_trade_time(item[3])
            )
            for item in data['data']
        ]

    def _handle_kline(self, data: dict, pair: str):
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

    def _handle_depth(self, data: dict, pair: str):
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
        received = datetime.utcfromtimestamp(data['data']['timestamp'] / 1000)
        depth = OkexSpotDepth(
            asks=asks,
            bids=bids,
            pair=pair,
            received=received
        )
