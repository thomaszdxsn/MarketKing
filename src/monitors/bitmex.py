"""
author: thomaszdxsn
"""
import collections
import json
from asyncio.locks import Lock

import arrow
from aiohttp import WSMessage

from . import MonitorAbstract
from ..sdk.bitmex import BitmexWebsocket
from ..schemas.markets import (BitmexTrade, BitmexTradeBin,
                               BitmexQuoteBin, BitmexDepth,
                               BitmexSettlement)

__all__ = ('BitmexMonitor',)


class BitmexMonitor(MonitorAbstract):
    exchange = 'bitmex'
    _ws_sdk_class = BitmexWebsocket

    def __init__(self, *args, **kwargs):
        super(BitmexMonitor, self).__init__(*args, **kwargs)
        self._instrument_books = collections.defaultdict(dict)  # TODO
        self._orderbooks = collections.defaultdict(dict)
        self._orderbooks_lock = Lock()

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_trade_bin(symbol)
            self.ws_sdk.register_trades(symbol)
            self.ws_sdk.register_quote_bin(symbol)
            self.ws_sdk.register_orderbook10(symbol)
        self.ws_sdk.register_settlement()
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)
        self.scheduler.add_job(self._transport_orderbook_snapshot,
                               trigger='cron',
                               second='*')

    async def dispatch_ws_msg(self, msg: WSMessage):
        data = json.loads(msg.data)
        table = data.get('table', '')
        if 'tradeBin' in table:
            await self._handle_trade_bin(data)
        elif 'quoteBin' in table:
            await self._handle_quote_bin(data)
        elif 'orderBook' in table:
            await self._handle_orderbook10(data)
        elif table == 'trade':
            await self._handle_trade(data)
        elif table == 'settlement':
            await self._handle_settlement(data)

    async def _handle_trade_bin(self, data: dict):
        trade_bin_list = [
            BitmexTradeBin(
                start_time=arrow.get(item['timestamp']).naive,
                pair=item['symbol'],
                open=item['open'],
                high=item['high'],
                low=item['low'],
                close=item['close'],
                trades=item['trades'],
                vol=item['volume'],
                vwap=item['vwap'],
                last_size=item['lastSize'],
                turnover=item['turnover'],
                home_notional=item['homeNotional'],
                foreign_notional=item['foreignNotional']
            )
            for item in data['data']
        ]
        [self.transport('trade_bin', i) for i in trade_bin_list]

    async def _handle_quote_bin(self, data: dict):
        quote_bin_list = [
            BitmexQuoteBin(
                pair=item['symbol'],
                start_time=arrow.get(item['timestamp']).naive,
                bid_size=item['bidSize'],
                bid_price=item['bidPrice'],
                ask_price=item['askPrice'],
                ask_size=item['askSize']
            )
            for item in data['data']
        ]
        [self.transport('quote_bin', i) for i in quote_bin_list]

    async def _handle_trade(self, data: dict):
        trades = [
            BitmexTrade(
                pair=item['symbol'],
                side=item['side'],
                size=item['size'],
                price=item['price'],
                tick_direction=item['tickDirection'],
                tid=item['trdMatchID'],
                gross_value=item['grossValue'],
                home_notional=item['homeNotional'],
                foreign_notional=item['foreignNotional'],
                trade_time=arrow.get(item['timestamp']).naive
            )
            for item in data['data']
        ]
        [self.transport('trade', i) for i in trades]

    async def _handle_settlement(self, data: dict):
        settlements = [
            BitmexSettlement(
                pair=item['symbol'],
                start_time=arrow.get(item['timestamp']).naive,
                settlement_type=item['settlementType'],
                settled_price=item['settledPrice'],
                option_strike_price=item['optionStrikePrice'],
                option_underlying_price=item['optionUnderlyingPrice'],
                bankrupt=item['bankrupt'],
                tax_base=item['taxBase'],
                tax_rate=item['taxRate']
            )
            for item in data['data']
        ]
        [self.transport('settlement', i) for i in settlements]

    async def _handle_orderbook10(self, data: dict):
        item = data['data'][0]
        symbol = item['symbol']
        async with self._orderbooks_lock:
            self._orderbooks[symbol].update(item)

    async def _transport_orderbook_snapshot(self):
        async with self._orderbooks_lock:
            for item in self._orderbooks.values():
                depth = self._format_orderbook10(item)
                self.transport('depth', depth)

    def _format_orderbook10(self, item: dict) -> BitmexDepth:
        depth = BitmexDepth(
            pair=item['symbol'],
            asks=[
                {'price': i[0], 'amount': i[1]}
                for i in item['asks']
            ],
            bids=[
                {'price': i[0], 'amount': i[1]}
                for i in item['bids']
            ],
            server_created=arrow.get(item['timestamp']).naive
        )
        return depth
