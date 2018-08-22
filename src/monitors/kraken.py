"""
author: thomaszdxsn
"""
import asyncio

import arrow

from . import MonitorAbstract
from ..sdk.kraken import KrakenRest

__all__ = (
    'KrakenMonitor',
)


class KrakenMonitor(MonitorAbstract):
    _rest_sdk_class = KrakenRest

    def __init__(self, *args, **kwargs):
        super(KrakenMonitor, self).__init__(*args, **kwargs)
        self.trades_interval = 300

    async def schedule(self):
        # await self._req_ticker()
        # await self._req_depth()
        await self._req_trades()

    async def _req_ticker(self):
        """一次性请求所有的symbols"""
        resp = await self.rest_sdk.get_ticker_async(self.symbols)
        if resp.error != 0:
            return

    async def _req_depth(self):
        await asyncio.gather(*[self._single_req_depth(symbol)
                               for symbol in self.symbols])

    async def _single_req_depth(self, symbol):
        resp = await self.rest_sdk.get_depth_async(symbol)
        if resp.error != 0:
            return
        print(resp)

    async def _req_trades(self):
        # TODO: 需要想办法能够拿下完整的trades
        # 现在每个请求最多发送1000个trades
        # 如果用定时任务，单位时间内交易量过大的时候会遗漏
        for symbol in self.symbols:
            await self._single_req_trades(symbol)
            await asyncio.sleep(2)

    async def _single_req_trades(self, symbol):
        resp = await self.rest_sdk.get_trades_async(symbol)
        if resp.error != 0:
            return



