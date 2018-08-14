"""
author: thomaszdxsn
"""
import json
from datetime import datetime

from . import MonitorAbstract
from ..sdk.binance import BinanceWebsocket, BinanceRest
from ..schemas.regexes import BINANCE_WS_CHANS
from ..schemas.markets import (BinanceTicker, BinanceTrades, 
                               BinanceKline, BinanceDepth)

__all__ = (
    'BinanceMonitor',
)


class BinanceMonitor(MonitorAbstract):
    _rest_sdk_class = BinanceRest
    _ws_sdk_class = BinanceWebsocket

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_depth(symbol)
            self.ws_sdk.register_trades(symbol)
            self.ws_sdk.register_kline(symbol)
            self.ws_sdk.register_ticker(symbol)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)

    def dispatch_ws_msg(self, msg):
        data = json.loads(msg.data)
        match_dict = BINANCE_WS_CHANS.match(data['stream']).groupdict()
        pair, data_type = match_dict['symbol'], match_dict['data_type']
        if 'ticker' in data_type:
            self._handle_ticker(data, pair)
        elif 'trade' in data_type:
            self._handle_trade(data, pair)
        elif 'depth' in data_type:
            self._handle_depth(data, pair)
        else:
            self._handle_kline(data, pair)

    def _handle_ticker(self, data: dict, pair: str):
        data_dict = data['data']
        ticker = BinanceTicker(
            event_time=datetime.utcfromtimestamp(data_dict['E'] / 1000),
            price_change=float(data_dict['p']),
            price_change_prec=float(data_dict['P']),
            close_amount=float(data_dict['Q']),
            bid=float(data_dict['b']),
            bbq=float(data_dict['B']),
            ask=float(data_dict['a']),
            baq=float(data_dict['A']),
            open=float(data_dict['o']),
            high=float(data_dict['h']),
            low=float(data_dict['l']),
            vol=float(data_dict['v']),
            quote_vol=float(data_dict['q']),
            open_time=datetime.utcfromtimestamp(data_dict['O'] / 1000),
            close_time=datetime.utcfromtimestamp(data_dict['C'] / 1000),
            first_trade_id=str(data_dict['F']),
            last_trade_id=str(data_dict['L']),
            total_trades=int(data_dict['n']),
            pair=pair
        )
 
    def _handle_trade(self, data: dict, pair: str):
        data_dict = data['data']
        trade = BinanceTrades(
            event_time=datetime.utcfromtimestamp(data_dict['E'] / 1000),
            tid=str(data_dict['t']),
            price=float(data_dict['p']),
            amount=float(data_dict['q']),
            buyer_order_id=str(data_dict['b']),
            seller_order_id=str(data_dict['a']),
            trade_time=datetime.utcfromtimestamp(data_dict['T'] / 1000),
            is_buyer_maker=data_dict['m'],
            direction=None,
            pair=pair
        )

    def _handle_depth(self, data: dict, pair: str):
        data_dict = data['data']
        asks = [
            {
                'price': float(item[0]),
                'amount': float(item[1])
            }
            for item in data_dict['asks']
        ]
        bids = [
            {
                'price': float(item[0]),
                'amount': float(item[1])
            }
            for item in data_dict['bids']
        ]
        depth = BinanceDepth(
            bids=bids,
            asks=asks,
            last_update_id=data_dict['lastUpdateId'],
            pair=pair
        )

    def _handle_kline(self, data: dict, pair: str):
        data_dict = data['data']
        kline_item = data_dict['k']
        kline = BinanceKline(
            event_time=datetime.utcfromtimestamp(data_dict['E'] / 1000),
            start_time=datetime.utcfromtimestamp(kline_item['t'] / 1000),
            first_trade_id=str(kline_item['f']),
            last_trade_id=str(kline_item['L']),
            open=float(kline_item['o']),
            close=float(kline_item['c']),
            high=float(kline_item['h']),
            low=float(kline_item['l']),
            vol=float(kline_item['v']),
            total_trades=int(kline_item['n']),
            is_completed=kline_item['x'],
            quote_vol=float(kline_item['q']),
            taker_base_vol=float(kline_item['V']),
            taker_quote_vol=float(kline_item['Q']),
            pair=pair
        )

