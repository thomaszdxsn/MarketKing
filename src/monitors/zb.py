"""
author: thomaszdxsn
"""
import asyncio
import json
from datetime import datetime

from aiohttp import WSMessage

from . import MonitorAbstract
from ..sdk.zb import ZBRest, ZBWebsocket
from ..schemas.markets import ZBTrades, ZBTicker, ZBDepth, ZBKline

__all__ = (
    'ZBMonitor',
)


class ZBMonitor(MonitorAbstract):
    exchange = 'zb'
    _ws_sdk_class = ZBWebsocket
    _rest_sdk_class = ZBRest

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_depth(symbol)
            self.ws_sdk.register_trades(symbol)
            self.ws_sdk.register_ticker(symbol)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)
        # 每10分钟运行一次，拿之前60条1分钟k线
        self.scheduler.add_job(
            self._req_kline,
            trigger='cron',
            args=(60,),
            minute='*/10'
        )

    async def dispatch_ws_msg(self, msg: WSMessage):
        data = json.loads(msg.data)
        data_type = data['dataType']
        pair = data['channel'].split('_')[0]
        if data_type == 'depth':
            await self._handle_depth(data, pair)
        elif data_type == 'ticker':
            await self._handle_ticker(data, pair)
        elif data_type == 'trades':
            await self._handle_trades(data, pair)

    async def _handle_trades(self, data: dict, pair: str):
        trades = [
            ZBTrades(
                pair=pair,
                amount=float(item['amount']),
                price=float(item['price']),
                direction=item['type'],
                tid=item['tid'],
                trade_time=datetime.utcfromtimestamp(item['date'])
            )
            for item in data['data']
        ]
        [self.transport('trades', t) for t in trades]

    async def _handle_ticker(self, data: dict, pair: str):
        tick_data = data['ticker']
        ticker = ZBTicker(
            pair=pair,
            server_created=datetime.utcfromtimestamp(int(data['date']) / 1000),
            vol=float(tick_data['vol']),
            high=float(tick_data['high']),
            low=float(tick_data['low']),
            last=float(tick_data['last']),
            ask=float(tick_data['sell']),
            bid=float(tick_data['buy'])
        )
        self.transport('ticker', ticker)

    async def _handle_depth(self, data: dict, pair: str):
        asks = [
            {
                'price': item[0],
                'amount': item[1]
            }
            for item in reversed(data['asks'])
        ]
        bids = [
            {
                'price': item[0],
                'amount': item[1]
            }
            for item in data['bids']
        ]
        depth = ZBDepth(
            asks=asks,
            bids=bids,
            pair=pair,
            server_created=datetime.utcfromtimestamp(data['timestamp'])
        )
        self.transport('depth', depth)

    async def _req_kline(self, size: int):
        """
        API文档说明: "3.K线接口每秒只能请求一次数据"
        所以，每个请求要间隔一秒
        """
        for symbol in self.symbols:
            await self._req_single_kline(symbol, size)
            await asyncio.sleep(1)

    async def _req_single_kline(self, symbol: str, size: int):
        kline_resp = await self.rest_sdk.get_kline_async(symbol, size=size)
        if kline_resp.error != 0:
            return
        data = kline_resp.data
        pair = f'{data["symbol"]}{data["moneyType"].lower()}'
        klines = [
            ZBKline(
                pair=pair,
                start_time=datetime.utcfromtimestamp(item[0] / 1000),
                open=item[1],
                high=item[2],
                low=item[3],
                close=item[4],
                vol=item[5]
            )
            for item in kline_resp.data['data']
        ]
        [self.transport('kline', k) for k in klines]
