"""
Author: thomaszdxsn
"""
import asyncio
from datetime import datetime
from urllib.parse import urljoin
from typing import Union, Callable

from . import WebsocketSdkAbstract, RestSdkAbstract
from ..schemas import Params

__all__ = (
    'GateIORest',
)


class GateIORest(RestSdkAbstract):
    """
    doc: https://gate.io/api2
    """
    base_url = 'https://data.gateio.io'
    _ticker_url = '/api2/1/ticker/{symbol}'
    _depth_url = '/api2/1/orderBook/{symbol}'
    _trades_url = '/api2/1/tradeHistory/{symbol}'
    _kline_url = '/api2/1/candlestick2/{symbol}'

    def _ticker_request(self, symbol: str) -> Params:
        url = urljoin(
            self.base_url, 
            self._ticker_url.format(symbol=symbol)
        )
        return Params(args=(url,))

    def _depth_request(self, symbol: str) -> Params:
        url = urljoin(
            self.base_url, 
            self._depth_url.format(symbol=symbol)
        )
        return Params(args=(url,))

    def _trades_request(self, 
                        symbol: str,
                        tid: Union[str, None]=None) -> Params:
        url = urljoin(
            self.base_url, 
            self._trades_url.format(symbol=symbol)
        )
        if tid:
            url = f"{url}/{tid}"
        return Params(args=(url,))

    def _kline_request(self,
                       symbol: str,
                       group_sec: int=60,
                       range_hour: int=1) -> Params:
        url = urljoin(
            self.base_url,
            self._kline_url.format(symbol=symbol)
        )
        request_data = {
            'params': {
                'group_sec': group_sec,
                'range_hour': range_hour
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )
    

class GateIOWebsocket(WebsocketSdkAbstract):
    """
    doc: https://gateio.io/docs/websocket/index.html
    """
    _servertime_id = 100
    _alternative_ws_url = 'wss://ws.gate.io/v3/'
    ws_url = 'wss://ws.gateio.io/v3/'

    async def subscribe(self, *args, **kwargs):
        if not self.ws_client:
            await self.setup_ws_client()
        # subscribe server time
        server_time_chann = {
            'id': self._servertime_id,
            'method': 'server.time',
            'params': []
        }
        await self.ws_client.send_json(server_time_chann)
        await super().subscribe(*args, **kwargs)

    async def connect(self, handler: Callable):
        # 这个ws接口需要重复request才会返回数据
        i = 1
        chan_nums = len(self.register_hub) + 1
        async for msg in self.ws_client:
            await handler(msg)
            if i % chan_nums == 0:      # TODO: 需要为每个数据类型配置不同的sleep时间
                await asyncio.sleep(1)  # TODO: need configify
                i = 0
                await self.subscribe()
            i += 1

    def register_ticker(self, 
                        market: str,
                        id_: int, 
                        period: int=86400):
        channel_info = {
            'id': id_,
            'method': 'ticker.query',
            'params': [market.upper(), period]
        }
        self.register_channel(channel_info)

    def register_depth(self,
                       market: str,
                       id_: int,
                       limit: int=20,
                       interval: str='0.000000000001'):
        channel_info = {
            'id': id_,
            'method': 'depth.query',
            'params': [market.upper(), limit, interval]
        }
        self.register_channel(channel_info)

    def register_trades(self,
                        market: str,
                        id_: int,
                        last_id: int=0,
                        limit: int=20):
        channel_info = {
            'id': id_,
            'method': 'trades.query',
            'params': [market.upper(), limit, last_id]
        }
        self.register_channel(channel_info)

    def register_kline(self,
                       market: str,
                       id_: int,
                       start: int=1,
                       end: Union[int, None]=None,
                       interval=60):
        if end is None:
            end = int(datetime.now().timestamp())
        channel_info = {
            'id': id_,
            'method': 'kline.query',
            'params': [market.upper(), start, end, interval]
        }
        self.register_channel(channel_info)