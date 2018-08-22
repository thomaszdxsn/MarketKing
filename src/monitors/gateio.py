"""
author: thomaszdxsn
"""
from aiohttp import WSMessage

from . import MonitorAbstract
from ..sdk.gateio import GateIORest, GateIOWebsocket


class GateIOMonitor(MonitorAbstract):
    _rest_sdk_class = GateIORest
    _ws_sdk_class = GateIOWebsocket

    async def schedule(self):
        chan_base_id = {
            'ticker': 10000,
            'depth': 10000,
            'trades': 10000,
            'kline': 10000
        }
        for index, symbol in enumerate(self.symbols):
            self.ws_sdk.register_ticker(symbol, chan_base_id['ticker'] + index)
            self.ws_sdk.register_depth(symbol, chan_base_id['depth'] + index)
            self.ws_sdk.register_trades(symbol, chan_base_id['trades'] + index)
            self.ws_sdk.register_kline(symbol, chan_base_id['kline'] + index)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)

    async def dispatch_ws_msg(self, msg: WSMessage):
        print(msg)