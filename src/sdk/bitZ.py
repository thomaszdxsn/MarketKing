"""
Author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import WebsocketSdkAbstract, RestSdkAbstract
from ..schemas import Params


class BitZRest(RestSdkAbstract):
    """
    doc: https://apidoc.bit-z.com/cn/
    """
    base_url = 'https://apiv2.bitz.com/'
    _ticker_url = '/Market/ticker'
    _depth_url = '/Market/depth'
    _trades_url = '/Market/order'
    _kline_url = '/Market/kline'
    _headers = {
        'User-Agent': 'Mozilla/5.0 \(Windows NT 6.1; WOW64\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/39.0.2171.71 Safari/537.36'
    }

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

    def _depth_request(self, symbol: str) -> Params:
        url = urljoin(self.base_url, self._depth_url)
        request_data = {
            'params': {
                'symbol': symbol
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

    def _kline_request(self, 
                       symbol: str,
                       resolution: str='1min',
                       size: int=60,
                       to: Union[int, None]=None) -> Params:
        url = urljoin(self.base_url, self._kline_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'size': size,
                'resolution': resolution,
            }
        } 
        if to is not None:
            request_data['params']['to'] = to
        return Params(
            args=(url,),
            kwargs=request_data
        )
                