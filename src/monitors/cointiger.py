"""
author: thomaszdxsn
"""
from datetime import datetime

from dynaconf import settings

from . import MonitorAbstract
from ..sdk.cointiger import CointigerRest, CointigerWebsocket
from ..schemas.regexes import COINTIGER_WS_CHANS
from ..schemas.markets import (CointigerTicker, CointigerDepth,
                               CointigerTrades, CointigerKline)

__all__ = (
    'CointigerMonitor',
)

ORDERBOOK_LEVEL = settings.as_int('ORDERBOOK_LEVEL')


class CointigerMonitor(MonitorAbstract):
    exchange = 'cointiger'
    _ws_sdk_class = CointigerWebsocket
    _rest_sdk_class = CointigerRest

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_depth(symbol)
            self.ws_sdk.register_trades(symbol)
            self.ws_sdk.register_kline(symbol)
            self.ws_sdk.register_ticker(symbol)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)

    async def dispatch_ws_msg(self, msg: dict):
        if msg.get('event_rep', '') == 'subed':
            return
        print(msg)
        channel = msg['channel']
        match_dict = COINTIGER_WS_CHANS.match(channel).groupdict()
        data_type = match_dict['data_type']
        pair = match_dict['symbol']
        if data_type == 'ticker':
            await self._handle_ticker(msg, pair)
        elif data_type == 'depth':
            await self._handle_depth(msg, pair)
        elif data_type == 'trade':
            await self._handle_trades(msg, pair)
        elif data_type == 'kline':
            await self._handle_kline(msg, pair)

    async def _handle_ticker(self, data: dict, pair: str):
        ticker = CointigerTicker(
            pair=pair,
            server_created=datetime.utcfromtimestamp(data['ts'] / 1000),
            **data['tick']
        )
        self.transport('ticker', ticker)

    async def _handle_depth(self,
                            data: dict,
                            pair: str,
                            size: int=ORDERBOOK_LEVEL):
        asks = [
            {
                'price': float(item[0]),
                'amount': float(item[1])
            }
            for item in data['tick']['asks'][:size]
        ]
        bids = [
            {
                'price': float(item[0]),
                'amount': float(item[1])
            }
            for item in data['tick']['buys'][:size]
        ]
        depth = CointigerDepth(
            pair=pair,
            asks=asks,
            bids=bids,
            server_created=datetime.utcfromtimestamp(data['ts'] / 1000)
        )
        self.transport('depth', depth)

    async def _handle_trades(self, data: dict, pair: str):
        trades = [
            CointigerTrades(
                pair=pair,
                direction=item['side'],
                vol=item['vol'],
                price=item['price'],
                tid=str(item['id']),
                amount=item['amount'],
                trade_time=datetime.utcfromtimestamp(item['ts'] / 1000)
            )
            for item in data['tick']['data']
        ]
        [self.transport('trades', t) for t in trades]

    async def _handle_kline(self, data: dict, pair: str):
        tick = data['tick']
        kline = CointigerKline(
            pair=pair,
            amount=tick['amount'],
            vol=tick['vol'],
            high=tick['high'],
            low=tick['low'],
            close=tick['close'],
            open=tick['open'],
            start_time=datetime.utcfromtimestamp(tick['id'])
        )
        self.transport('kline', kline)