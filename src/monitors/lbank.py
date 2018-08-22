"""
author: thomaszdxsn
"""
from aiohttp import WSMessage

from . import MonitorAbstract
from ..sdk.lbank import LBankRest, LBankWebsocket

__all__ = (
    'LBankMonitor',
)


class LBankMonitor(MonitorAbstract):
    _ws_sdk_class = LBankWebsocket
    _rest_sdk_class = LBankRest

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_depth(symbol)
            self.ws_sdk.register_trades(symbol)
            self.ws_sdk.register_ticker(symbol)
            self.ws_sdk.register_kline(symbol)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)

    async def dispatch_ws_msg(self, msg: WSMessage):
        print(msg)
