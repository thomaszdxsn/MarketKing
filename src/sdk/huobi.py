"""
author: thomaszdxsn
"""
import gzip
import json
import random
from urllib.parse import urljoin
from typing import Callable

from . import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas import Params

__all__ = (
    'HuobiRest',
    'HuobiWebsocket'
)


class HuobiRest(RestSdkAbstract):
    base_url = 'https://api.huobi.pro/'
    _kline_url = '/market/history/kline'
    _trades_url = '/market/trade'
    _ticker_url = '/market/detail'
    _depth_url = '/market/depth'

    def _depth_request(self, symbol: str, type_: str='step0') -> Params:
        url = urljoin(self.base_url, self._depth_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'type': type_
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _ticker_request(self, symbol: str) -> Params:
        url = urljoin(self.base_url, self._ticker_url)
        request_data = {
            'params': {
                'symbol': symbol
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _kline_request(self,
                       symbol: str,
                       period: str='1min',
                       size: int=150) -> Params:
        url = urljoin(self.base_url, self._kline_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'period': period,
                'size': size
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _trades_request(self, symbol: str) -> Params:
        url = urljoin(self.base_url, self._trades_url)
        request_data = {
            'params': {
                'symbol': symbol
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )


class HuobiWebsocket(WebsocketSdkAbstract):
    ws_url = 'wss://api.huobi.pro/ws'

    def _gen_random_id(self) -> str:
        if not getattr(self, '_id_bucket', None):
            self._id_bucket = set()
        while True:
            random_id = str(random.randint(1, 10000))
            if random_id not in self._id_bucket:
                self._id_bucket.add(random_id)
                return random_id

    def register_kline(self, symbol: str, period: str='1min'):
        channel_info = {
            'sub': f"market.{symbol}.kline.{period}",
            'id': self._gen_random_id()
        }
        self.register_channel(channel_info)

    def register_depth(self, symbol: str, type_: str='step0'):
        channel_info = {
            'sub': f"market.{symbol}.depth.{type_}",
            "id": self._gen_random_id()
        }
        self.register_channel(channel_info)

    def register_trades(self, symbol: str):
        channel_info = {
            'sub': f"market.{symbol}.trade.detail",
            'id': self._gen_random_id()
        }
        self.register_channel(channel_info)

    def register_ticker(self, symbol: str):
        channel_info = {
            'sub': f"market.{symbol}.detail",
            "id": self._gen_random_id()
        }
        self.register_channel(channel_info)

    async def connect(self, handler: Callable):
         async for msg in self.ws_client:
             # TODO: handle error
             raw_data = gzip.decompress(msg.data)
             data = json.loads(raw_data, encoding='ascii')
             ping = data.get('ping')
             if ping:
                 await self.ws_client.send_json({
                     'pong': ping
                 })
                 continue
             handler(data)
