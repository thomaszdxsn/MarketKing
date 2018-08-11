"""
Author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

import arrow

from . import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas import Params

__all__ = (
    'KucoinRest',
)


class KucoinRest(RestSdkAbstract):
    """
    doc: https://kucoinapidocs.docs.apiary.io/#introduction/general
    """
    base_url = 'https://api.kucoin.com/'
    _ticker_url = '/v1/open/tick'
    _depth_url = '/v1/open/orders'
    _trades_url = '/v1/open/deal-orders'
    _kline_url = '/v1/open/kline'

    _headers = {
        "Accept-Language": "zh_CN"
    }

    def _ticker_request(self, symbol: str) -> Params:
        url = urljoin(self.base_url, self._ticker_url)
        request_data = {
            'params': {
                'symbol': symbol.upper()
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )
    
    def _depth_request(self, 
                       symbol: str,
                       limit: int=20,
                       group: Union[int, None]=None,
                       direction: Union[str, None]=None) -> Params:
        url = urljoin(self.base_url, self._depth_url)
        request_data = {
            'params': {
                'symbol': symbol.upper(),
                'limit': limit
            }
        }
        if group is not None:
            request_data['params']['group'] = group
        if direction is not None:
            assert direction in ('BUY', 'SELL'), \
                    'direction must be one of BUY or SELL'
            request_data['params']['direction'] = direction
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _trades_request(self,
                        symbol: str,
                        limit: Union[int, None]=None,
                        since: Union[int, None]=None) -> Params:
        url = urljoin(self.base_url, self._trades_url)
        request_data = {
            'params': {
                'symbol': symbol.upper(),
            }
        }
        if limit is not None:
            request_data['params']['limit'] = limit
        if since is not None:
            request_data['params']['since'] = since
        return Params(
            args=(url,),
            kwargs=request_data
        ) 

    def _kline_request(self,
                       symbol: str,
                       type_: str='1min',
                       from_: Union[int, None]=None,
                       to: Union[int, None]=None,
                       limit: int=60) -> Params:
        utcnow = arrow.utcnow()
        if from_ is None:
            from_ = utcnow.shift(minutes=-60).timestamp
        if to is None:
            to = utcnow.timestamp
        url = urljoin(self.base_url, self._kline_url)
        request_data = {
            'params': {
                'symbol': symbol.upper(),
                'limit': limit,
                'from': from_,
                'to': to,
                'type': type_
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )