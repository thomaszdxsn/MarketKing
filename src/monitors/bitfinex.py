"""
author: thomaszdxsn
"""
import collections
import json
from datetime import datetime
from typing import Callable, Union, Dict

from aiohttp import WSMessage

from . import MonitorAbstract
from ..sdk.bitfinex import BitfinexWebsocket, BitfinexRest
from ..schemas.markets import (BitfinexTradeTicker, BitfinexFundingTicker,
                               BitfinexTradeTrades, BitfinexFundingTrades,
                               BitfinexKline, BitfinexFundingOrderbook,
                               BitfinexTradeOrderbook)

__all__ = (
    'BitfinexMonitor',
)

ORDERBOOK_TYPE = Union[BitfinexTradeOrderbook, BitfinexFundingOrderbook]
ORDERBOOKS_DICT = Dict[str, ORDERBOOK_TYPE]


class BitfinexMonitor(MonitorAbstract):
    _rest_sdk_class = BitfinexRest
    _ws_sdk_class = BitfinexWebsocket

    def __init__(self, *args, **kwargs):
        super(BitfinexMonitor, self).__init__(*args, **kwargs)
        self.channel_hub = collections.defaultdict(dict)
        self.orderbooks: ORDERBOOKS_DICT=dict()

    def _register_callback(self,
                           chan_id: int,
                           callback: Callable,
                           symbol: str):
        self.channel_hub[chan_id]['callback'] = callback
        self.channel_hub[chan_id]['symbol'] = symbol

    def _parse_channel(self, channel: str, channel_id: int, symbol: str):
        if channel == 'ticker':
            self._register_callback(channel_id,
                                    self._handle_ticker,
                                    symbol)
        elif channel == 'candles':
            self._register_callback(channel_id,
                                    self._handle_kline,
                                    symbol,)
        elif channel == 'trades':
            self._register_callback(channel_id,
                                    self._handle_trades,
                                    symbol)
        else:
            self._register_callback(channel_id,
                                    self._handle_depth,
                                    symbol)

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_depth(symbol)
            self.ws_sdk.register_trades(symbol)
            self.ws_sdk.register_ticker(symbol)
            # funding数据暂时没有k线
            self.ws_sdk.register_kline(symbol)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)

    async def dispatch_ws_msg(self, msg: WSMessage):
        data = json.loads(msg.data)
        if isinstance(data, dict):
            self._log_sub_msg(data)
            if data.get('code', 0) == 20051:
                raise RuntimeError(data)
            event = data['event']
            if event != 'subscribed':
                return
            channel = data['channel']
            channel_id = data['chanId']
            symbol = (data.get('symbol')
                      if data.get('symbol') else data['key'].split(':')[-1])
            self._parse_channel(channel, channel_id, symbol)
        else:
            is_hb = isinstance(data[1], str) and data[1] == 'hb'
            if is_hb:
                return
            channel_id = data[0]
            channel_info = self.channel_hub[channel_id]
            symbol, callback = channel_info['symbol'], channel_info['callback']
            await callback(data, symbol)

    async def _handle_ticker(self, data: list, pair: str):
        item = data[1]
        if pair.startswith('t'):
            ticker = self.__gen_trade_ticker(item, pair)
        else:
            ticker = self.__gen_funding_ticker(item, pair)

    def __gen_trade_ticker(self,
                           data: list,
                           pair: str) -> BitfinexTradeTicker:
        return BitfinexTradeTicker(
            pair=pair,
            bid=data[0],
            bid_size=data[1],
            ask=data[2],
            ask_size=data[3],
            daily_change=data[4],
            daily_change_prec=data[5],
            last=data[6],
            vol=data[7],
            high=data[8],
            low=data[9]
        )

    def __gen_funding_ticker(self,
                             data: list,
                             pair: str) -> BitfinexFundingTicker:
        return BitfinexFundingTicker(
            pair=pair,
            frr=data[0],
            bid=data[1],
            bid_period=data[2],
            bid_size=data[3],
            ask=data[4],
            ask_period=data[5],
            ask_size=data[6],
            daily_change=data[7],
            daily_change_prec=data[8],
            last=data[9],
            vol=data[10],
            high=data[11],
            low=data[12]
        )

    async def _handle_trades(self, data: list, pair: str):
        type_ = data[1]
        if not isinstance(type_, str):
            return
        item = data[2]
        if pair.startswith('t'):
            trade = self.__gen_trade_trades(type_, item, pair)
        else:
            trade = self.__gen_funding_trades(type_, item, pair)

    def __gen_trade_trades(self,
                           type_: str,
                           data: list,
                           pair: str) -> BitfinexTradeTrades:
        return BitfinexTradeTrades(
            pair=pair,
            type=type_,
            tid=str(data[0]),
            trade_time=datetime.utcfromtimestamp(data[1] / 1000),
            amount=data[2],
            price=data[3]
        )

    def __gen_funding_trades(self,
                             type_: str,
                             data: list,
                             pair: str) -> BitfinexFundingTrades:
        return BitfinexFundingTrades(
            pair=pair,
            type=type_,
            tid=str(data[0]),
            trade_time=datetime.utcfromtimestamp(data[1] / 1000),
            amount=data[2],
            rate=data[3],
            period=data[4]
        )

    async def _handle_kline(self, data: list, pair: str):
        item = data[1]
        if not item:
            return
        if isinstance(item[0], list):
            # process list
            kline = [self.__gen_kline(i, pair) for i in item]
        else:
            kline = self.__gen_kline(item, pair)

    def __gen_kline(self, data: list, pair: str) -> BitfinexKline:
        return BitfinexKline(
            pair=pair,
            start_time=datetime.utcfromtimestamp(data[0] / 1000),
            open=data[1],
            close=data[2],
            high=data[3],
            low=data[4],
            vol=data[5]
        )

    async def _handle_depth(self, data: list, pair: str):
        data_list = data[1]
        is_snapshot = isinstance(data_list[0], list)
        if is_snapshot:
            if pair.startswith('f'):
                self.orderbooks[pair] = BitfinexFundingOrderbook(data_list)
            else:
                self.orderbooks[pair] = BitfinexTradeOrderbook(data_list)
        else:
            self.orderbooks[pair].update(data_list)


