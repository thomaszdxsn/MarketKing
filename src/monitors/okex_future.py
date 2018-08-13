"""
author: thomaszdxsn
"""
import itertools
import json

from aiohttp import WSMsgType

from . import MonitorAbstract
from ..schemas.regexes import OKEX_FUTURE_WS_CHANS
from ..sdk.okex_future import (OkexFutureRest, OkexFutureWebsocket,
                               CONTRACT_TYPES)


class OkexFutureMonitor(MonitorAbstract):
    _rest_sdk_class = OkexFutureRest
    _ws_sdk_class = OkexFutureWebsocket

    async def schedule(self):
        combinations = itertools.product(self.symbols, CONTRACT_TYPES)
        for symbol, contract_type in combinations:
            self.ws_sdk.register_ticker(symbol, contract_type=contract_type)
            self.ws_sdk.register_depth(symbol, contract_type=contract_type)
            self.ws_sdk.register_trades(symbol, contract_type=contract_type)
            self.ws_sdk.register_kline(symbol, contract_type=contract_type)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)

    def dispatch_ws_msg(self, msg):
        if msg.type != WSMsgType.TEXT:
            return
        data = json.loads(msg.data)[0]
        channel = data['channel']
        if channel == 'addChannel':
            return

        match_dict = OKEX_FUTURE_WS_CHANS.match(channel).groupdict()
        data_type, symbol, contract_type = (match_dict['data_type'],
                                            match_dict['symbol'],
                                            match_dict['contract_type'])

        if data_type == 'trade':
            self._handle_trades(data, symbol, contract_type)
        elif data_type == 'kline':
            self._handle_kline(data, symbol, contract_type)
        elif data_type == 'depth':
            self._handle_depth(data, symbol, contract_type)
        else:
            self._handle_ticker(data, symbol, contract_type)

    def _handle_depth(self, data: dict, symbol: str, contract_type: str):
        print(data)

    def _handle_ticker(self, data: dict, symbol: str, contract_type: str):
        pass

    def _handle_kline(self, data: dict, symbol: str, contract_type: str):
        pass

    def _handle_trades(self, data: dict, symbol: str, contract_type: str):
        pass
