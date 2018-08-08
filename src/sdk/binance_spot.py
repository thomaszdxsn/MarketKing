"""
author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import WebsocketSdkAbstract, RestSdkAbstract
from ..schemas import Params


class BinanceSpotRest(RestSdkAbstract):
    """
    doc: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md
    """
    base_url = 'https://api.binance.com'
    _depth_url = '/api/v1/depth'
    _24h_ticker_url = '/api/v1/ticker/24hr'
    _kline_url = '/api/v1/klines'
    _trades_url = '/api/v1/trades'

    def _depth_request(self, symbol: str, limit: int=100) -> Params:
        url = urljoin(self.base_url, self._depth_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'limit': limit
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _ticker_request(self, symbol: str) -> Params:
        """24h ticker"""
        url = urljoin(self.base_url, self._24h_ticker_url)
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
                       interval: str='1m',
                       start_time: Union[int, None]=None,
                       end_time: Union[int, None]=None,
                       limit: int=500) -> Params:
        url = urljoin(self.base_url, self._kline_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
        }
        if start_time is not None:
            request_data['params']['startTime'] = start_time
        if end_time is not None:
            request_data['params']['endTime'] = end_time
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _trades_request(self, symbol: str, limit: int=500) -> Params:
        url = urljoin(self.base_url, self._trades_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'limit': limit
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )