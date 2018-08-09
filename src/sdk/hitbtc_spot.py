"""
Author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas import Params


class HitBTCSpotRest(RestSdkAbstract):
    """
    doc: https://api.hitbtc.com/?python#development-guide
    """
    base_url = 'https://api.hitbtc.com/'
    _ticker_url = '/api/2/public/ticker/{symbol}'
    _trades_url = '/api/2/public/trades/{symbol}'
    _depth_url = '/api/2/public/orderbook/{symbol}'
    _kline_url = '/api/2/public/candles/{symbol}'

    def _ticker_request(self, symbol: str) -> Params:
        url = urljoin(
            self.base_url,
            self._ticker_url.format(symbol=symbol.upper())
        )
        return Params(
            args=(url,)
        )
    
    def _trades_request(self, 
                        symbol: str,
                        sort: str='DESC',
                        by: str='timestamp',
                        from_: Union[int, None]=None,
                        till: Union[int, None]=None,
                        limit: Union[int, None]=None,
                        offset: Union[int, None]=None) -> Params:
        url = urljoin(
            self.base_url,
            self._trades_url.format(symbol=symbol.upper())
        )
        request_data = {
            'params': {
                'sort': sort,
                'by': by
            }
        }
        if from_ is not None:
            request_data['params']['form'] = form_
        if till is not None:
            request_data['params']['till'] = till
        if limit is not None:
            request_data['params']['limit'] = limit
        if offset is not None:
            request_data['params']['offset'] = offset
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _depth_request(self, 
                       symbol: str,
                       limit: int=100) -> Params:
        url = urljoin(
            self.base_url,
            self._depth_url.format(symbol=symbol.upper())
        )
        request_data = {
            'params': {
                'limit': limit
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _kline_request(self,
                       symbol: str,
                       limit: int=100,
                       period: str='M1') -> Params:
        url = urljoin(
            self.base_url,
            self._kline_url.format(symbol=symbol.upper())
        )
        request_data = {
            'params': {
                'limit': limit,
                'period': period
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        ) 
    

class HitBTCSpotWebsocket(WebsocketSdkAbstract):
    ws_url = 'wss://api.hitbtc.com/api/2/ws'

    def register_ticker(self, symbol: str):
        channel_info = {
            'method': 'subscribeTicker',
            'params': {
                'symbol': symbol.upper()
            },
            'id': '1'
        }
        self.register_channel(channel_info)

    def register_depth(self, symbol: str):
        channel_info = {
            'method': 'subscribeOrderbook',
            'params': {
                'symbol': symbol.upper()
            },
            'id': '1'
        }
        self.register_channel(channel_info)

    def register_trades(self, symbol: str):
        channel_info = {
            'method': 'subscribeTrades',
            'params': {
                'symbol': symbol.upper()
            },
            'id': '1'
        }
        self.register_channel(channel_info)

    def register_kline(self, symbol: str, period: str='M1'):
        channel_info = {
            'method': 'subscribeCandles',
            'params': {
                'symbol': symbol.upper(),
                'period': period
            },
            'id': '1'
        }
        self.register_channel(channel_info)