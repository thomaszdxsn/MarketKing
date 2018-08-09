"""
author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas import Params

__all__ = (
    'FcoinRest',
    'FcoinWebsocket'
)


class FcoinRest(RestSdkAbstract):
    """
    doc: https://developer.fcoin.com/zh.html
    """
    base_url = 'https://api.fcoin.com/'
    _ticker_url = '/v2/market/ticker/{symbol}'
    _depth_url = '/v2/market/depth/{level}/{symbol}'
    _trades_url = '/v2/market/trades/{symbol}'
    _kline_url = '/v2/market/candles/{resolution}/{symbol}'

    def _ticker_request(self, symbol: str) -> Params:
        url = urljoin(self.base_url,
                      self._ticker_url.format(symbol=symbol))
        return Params(args=(url,))

    def _depth_request(self, symbol: str, level: str='L20') -> Params:
        url = urljoin(
            self.base_url,
            self._depth_url.format(
                symbol=symbol,
                level=level
            )
        )
        return Params(args=(url,))

    def _trades_request(self,
                        symbol: str,
                        before: Union[str, None]=None,
                        limit: int=20) -> Params:
        url = urljoin(
            self.base_url,
            self._trades_url.format(
                symbol=symbol
            )
        )
        request_data = {
            'params': {
                'limit': limit
            }
        }
        if before is not None:
            request_data['params']['before'] = before
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _kline_request(self,
                       symbol: str,
                       resolution: str='M1',
                       before: Union[str, None]=None,
                       limit: int=20) -> Params:
        url = urljoin(
            self.base_url,
            self._kline_url.format(
                symbol=symbol,
                resolution=resolution
            )
        )
        request_data = {
            'params': {
                'limit': limit
            }
        }
        if before is not None:
            request_data['params']['before'] = before
        return Params(
            args=(url,),
            kwargs=request_data
        )


class FcoinWebsocket(WebsocketSdkAbstract):
    ws_url = 'wss://api.fcoin.com/v2/ws'

    def register_ticker(self, symbol: str):
        channel_info = {
            'cmd': 'sub',
            'args': [f"ticker.{symbol}"],
            'id': '1'
        }
        self.register_channel(channel_info)

    def register_depth(self, symbol: str, level: str='L20'):
        channel_info = {
            'cmd': 'sub',
            'args': [f"depth.{level}.{symbol}"],
            'id': '1'
        }
        self.register_channel(channel_info)

    def register_kline(self, symbol: str, resolution: str='M1'):
        channel_info = {
            'cmd': 'sub',
            'args': [f"candle.{resolution}.{symbol}"],
            'id': '1'
        }
        self.register_channel(channel_info)

    def register_trades(self, symbol: str, limit: int=20):
        channel_info = {
            'cmd': 'sub',
            'args': [f"trade.{symbol}"],
            'id': '1'
        }
        self.register_channel(channel_info)
