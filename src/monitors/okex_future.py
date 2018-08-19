"""
author: thomaszdxsn
"""
import itertools
import json
import collections
from datetime import datetime
from asyncio.locks import Lock

import arrow
from aiohttp import WSMsgType

from . import MonitorAbstract
from ..schemas.regexes import OKEX_FUTURE_WS_CHANS
from ..schemas.markets import (OkexFutureDepth, OkexFutureTicker,
                               OkexFutureKline, OkexFutureTrades)
from ..sdk.okex_future import (OkexFutureRest, OkexFutureWebsocket,
                               CONTRACT_TYPES)

__all__ = (
    'OkexFutureMonitor',
)


class OkexFutureMonitor(MonitorAbstract):
    exchange = 'okex_future'
    _rest_sdk_class = OkexFutureRest
    _ws_sdk_class = OkexFutureWebsocket

    def __init__(self, *args, **kwargs):
        super(OkexFutureMonitor, self).__init__(*args, **kwargs)
        self._orderbooks = collections.defaultdict(dict)
        self._orderbooks_lock = Lock()
        self._orderbooks_key_sep = '|'
        self._orderbooks_use_snapshots = False

    async def schedule(self):
        combinations = itertools.product(self.symbols, CONTRACT_TYPES)
        for symbol, contract_type in combinations:
            self.ws_sdk.register_ticker(symbol, contract_type=contract_type)
            self.ws_sdk.register_depth(symbol, contract_type=contract_type)
            self.ws_sdk.register_trades(symbol, contract_type=contract_type)
            self.ws_sdk.register_kline(symbol, contract_type=contract_type)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)
        if self._orderbooks_use_snapshots:
            # 按秒级别进行depth快照
            self.scheduler.add_job(self._transport_depth_snapshots,
                                   trigger='cron',
                                   second='*')

    async def dispatch_ws_msg(self, msg):
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
            await self._handle_trades(data, symbol, contract_type)
        elif data_type == 'kline':
            await self._handle_kline(data, symbol, contract_type)
        elif data_type == 'depth':
            await self._handle_depth(data, symbol, contract_type)
        else:
            await self._handle_ticker(data, symbol, contract_type)

    def __handle_depth_item(self, item: list) -> dict:
        return {
            'price': float(item[0]),
            'sheet_quantity': float(item[1]),
            'token_quantity': float(item[2]),
            'sheet_cumulant': float(item[3]),
            'token_cumulant': float(item[4])
        }

    async def _handle_depth(self, data: dict, symbol: str, contract_type: str):
        if self._orderbooks_use_snapshots:
            async with self._orderbooks_lock:
                key = f'{symbol}{self._orderbooks_key_sep}{contract_type}'
                self._orderbooks[key].update(data)
        else:
            depth = self._format_depth(data, symbol, contract_type)
            self.transport('depth', depth)

    async def _transport_depth_snapshots(self):
        async with self._orderbooks_lock:
            for key, data in self._orderbooks.items():
                symbol, contract_type = key.split(self._orderbooks_key_sep)
                depth = self._format_depth(data, symbol, contract_type)
                self.transport('depth', depth)

    def _format_depth(self,
                            data: dict,
                            symbol: str,
                            contract_type: str) -> OkexFutureDepth:
        asks = [
            self.__handle_depth_item(item)
            for item in reversed(data['data']['asks'])
        ]
        bids = [
            self.__handle_depth_item(item)
            for item in data['data']['bids']
        ]
        server_created = datetime.utcfromtimestamp(
            data['data']['timestamp'] / 1000
        )
        depth = OkexFutureDepth(
            asks=asks,
            bids=bids,
            pair=symbol,
            server_created=server_created,
            contract_type=contract_type
        )
        return depth

    async def _handle_ticker(self, data: dict, symbol: str, contract_type: str):
        data_dict = data['data']
        ticker = OkexFutureTicker(
            pair=symbol,
            contract_type=contract_type,
            high=float(data_dict['high']),
            limit_low=float(data_dict['limitLow']),
            vol=float(data_dict['vol']),
            last=float(data_dict['last']),
            low=float(data_dict['low']),
            ask=float(data_dict['sell']),
            bid=float(data_dict['buy']),
            hold_amount=float(data_dict['hold_amount']),
            contract_id=str(data_dict['contractId']),
            unit_amount=float(data_dict['unitAmount']),
            limit_high=float(data_dict['limitHigh'])
        )
        self.transport('ticker', ticker)

    async def _handle_kline(self, data: dict, symbol: str, contract_type: str):
        data_lst = data['data']
        klines = [
            OkexFutureKline(
                pair=symbol,
                contract_type=contract_type,
                start_time=datetime.utcfromtimestamp(int(item[0]) / 1000),
                open=float(item[1]),
                high=float(item[2]),
                low=float(item[3]),
                close=float(item[4]),
                sheet_vol=float(item[5]),
                vol=float(item[6])
            )
            for item in data_lst
        ]
        list(map(
            lambda x: self.transport('kline', x),
            klines
        ))

    def __format_trade_time(self, trade_time: str) -> datetime:
        """
        '06:58:33' -> utc datetime
        # TODO: 这个方法不太适用，需要时刻保持时区和okex交易所一致
        """
        hour, minute, second = trade_time.split(':')
        return arrow.now().to('Asia/Shanghai').replace(
            hour=int(hour),
            minute=int(minute),
            second=int(second)
        ).to('UTC').naive

    async def _handle_trades(self, data: dict, symbol: str, contract_type: str):
        trades = [
            OkexFutureTrades(
                pair=symbol,
                contract_type=contract_type,
                tid=item[0],
                price=float(item[1]),
                amount=float(item[2]),
                direction=item[4],
                trade_time=item[3]
            )
            for item in data['data']
        ]
        list(map(
            lambda x: self.transport('trades', x),
            trades
        ))
