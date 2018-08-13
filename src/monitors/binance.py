"""
author: thomaszdxsn
"""
import json

from . import MonitorAbstract
from ..sdk.binance import BinanceWebsocket, BinanceRest
from ..schemas.regexes import BINANCE_WS_CHANS

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
        pair, data_type = match_dict['pair'], match_dict['data_type']
        if 'ticker' in data_type:
            self._handle_ticker(data, pair)
        elif 'trade' in data_type:
            self._handle_trade(data, pair)
        elif 'depth' in data_type:
            self._handle_depth(data, pair)
        else:
            self._handle_kline(data, pair)

    def _handle_ticker(self, data: dict, pair: str):
        pass

    def _handle_trade(self, data: dict, pair: str):
        pass

    def _handle_depth(self, data: dict, pair: str):
        pass

    def _handle_kline(self, data: dict, pair: str):
        pass

