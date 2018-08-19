"""
author: thomaszdxsn
"""
import asyncio
from datetime import datetime

import arrow

from . import MonitorAbstract
from ..sdk.bithumb import BithumbRest
from ..schemas.markets import BithumbTicker, BithumbDepth, BithumbTrades

__all__ = (
    'BithumbMonitor',
)


class BithumbMonitor(MonitorAbstract):
    exchange = 'bithumb'
    _rest_sdk_class = BithumbRest

    def __init__(self, *args, **kwargs):
        super(BithumbMonitor, self).__init__(*args, **kwargs)
        self.symbols_set = set(self.symbols)

    async def schedule(self):
        self.scheduler.add_job(
            self._req_depth,
            trigger='cron',
            second=f'*/{self._depth_interval}'
        )
        self.scheduler.add_job(
            self._req_ticker,
            trigger='cron',
            second=f'*/{self._ticker_interval}'
        )
        self.scheduler.add_job(
            self._req_trades,
            trigger='cron',
            second='*/20'
        )

    async def _req_ticker(self):
        ticker_resp = await self.rest_sdk.get_ticker_async()
        if ticker_resp.error != 0:
            return
        ticker_data = ticker_resp.data['data']
        for symbol, value in ticker_data.items():
            if symbol not in self.symbols_set:
                continue
            ticker = BithumbTicker(
                pair=symbol,
                close=float(value['closing_price']),
                open=float(value['opening_price']),
                low=float(value['min_price']),
                high=float(value['max_price']),
                avg_price=float(value['average_price']),
                units_traded=float(value['units_traded']),
                vol_1day=float(value['volume_1day']),
                vol_7day=float(value['volume_7day']),
                bid=float(value['buy_price']),
                ask=float(value['sell_price']),
                change=float(value['24H_fluctate']),
                change_perc=float(value['24H_fluctate_rate']),
                server_created=datetime.utcfromtimestamp(
                    int(ticker_data['date']) / 1000
                )
            )
            self.transport('ticker', ticker)

    async def _req_depth(self):
        depth_resp = await self.rest_sdk.get_depth_async()
        if depth_resp.error != 0:
            return
        depth_data = depth_resp.data['data']
        for symbol, value in depth_data.items():
            if symbol not in self.symbols_set:
                continue
            asks = [
                {
                    'price': float(item['price']),
                    'amount': float(item['quantity'])
                }
                for item in value['asks']
            ]
            bids = [
                {
                    'price': float(item['price']),
                    'amount': float(item['quantity'])
                }
                for item in value['bids']
            ]
            depth = BithumbDepth(
                asks=asks,
                bids=bids,
                server_created=datetime.utcfromtimestamp(
                    int(depth_data['timestamp']) / 1000
                ),
                pair=symbol
            )
            self.transport('depth', depth)

    async def _req_trades(self):
        await asyncio.gather(*[
            self._req_singe_trades(symbol)
            for symbol in self.symbols
        ])

    async def _req_singe_trades(self, symbol: str):
        trade_resp = await self.rest_sdk.get_trades_async(symbol)
        if trade_resp.error != 0:
            return
        for item in trade_resp.data['data']:
            trade = BithumbTrades(
                pair=symbol,
                tid=item['cont_no'],
                trade_time=arrow.get(item['transaction_date']).naive,
                direction=item['type'],
                units_traded=float(item['units_traded']),
                price=float(item['price']),
                amount=float(item['total'])
            )
            self.transport('trades', trade)
