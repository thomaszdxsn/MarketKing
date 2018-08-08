"""
author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas import Params


class OkexSpotRest(RestSdkAbstract):
    base_url = 'https://www.okex.com/api/v1/'
    _ticker_url = '/api/v1/ticker.do'
    _depth_url = '/api/v1/depth.do'
    _trades_url = '/api/v1/trades.do'
    _kline_url = '/api/v1/kline.do'

    headers = {
        'ContentType': 'application/x-www-form-urlencoded'
    }

    def _ticker_request(self, symbol: str) -> Params:
        url = urljoin(self.base_url, self._ticker_url)
        request_data = {
            'params': {
                'symbol': symbol
            },
            'headers': self.headers
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _depth_request(self,
                       symbol: str,
                       size: int=200) -> Params:
        url = urljoin(self.base_url, self._depth_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'size': size
            },
            'headers': self.headers
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _trades_request(self,
                        symbol: str,
                        since: Union[int, None]=None) -> Params:
        url = urljoin(self.base_url, self._trades_url)
        request_data = {
            'params': {
                'symbol': symbol,
            },
            'headers': self.headers
        }
        if since is not None:
            request_data['params']['since'] = since
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _kline_request(self,
                       symbol: str,
                       type_: str,
                       size: Union[int, None]=None,
                       since: Union[int, None]=None) -> Params:
        url = urljoin(self.base_url, self._kline_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'type': type_
            },
            'headers': self.headers
        }
        if size:
            request_data['params']['size'] = size
        if since:
            request_data['params']['since'] = since
        return Params(
            args=(url,),
            kwargs=request_data
        )


class OkexSpotWebsocket(WebsocketSdkAbstract):
    ws_url = 'wss://real.okex.com:10441/websocket'

    def register_ticker(self, symbol: str):
        channel_info = {
            'event': 'addChannel',
            'channel': f'ok_sub_spot_{symbol}_ticker'
        }
        self.register_channel(channel_info)

    def register_depth(self, symbol: str, size: int=20):
        channel_info = {
            'event': 'addChannel',
            'channel': f'ok_sub_spot_{symbol}_depth_{size}'
        }
        self.register_channel(channel_info)

    def register_trades(self, symbol: str):
        channel_info = {
            'event': 'addChannel',
            'channel': f'ok_sub_spot_{symbol}_deals'
        }
        self.register_channel(channel_info)

    def register_kline(self, symbol: str, type_: str='1min'):
        channel_info = {
            'event': 'addChannel',
            'channel': f'ok_sub_spot_{symbol}_kline_{type_}'
        }
        self.register_channel(channel_info)
