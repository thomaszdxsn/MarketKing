"""
author: thomaszdxsn
"""
from datetime import datetime
from urllib.parse import urljoin
from typing import Union

from . import RestSdkAbstract
from ..schemas import Params

__all__ = (
    'UpbitRest',
)


class UpbitRest(RestSdkAbstract):
    """
    doc: https://docs.upbit.com/v1.0/reference
    """
    base_url = 'https://api.upbit.com/'
    _ticker_url = '/v1/ticker'
    _kline_url = '/v1/candles/minutes/{unit}'
    _trades_url = '/v1/trades/ticks'
    _depth_url = '/v1/orderbook'

    def _ticker_request(self, markets: Union[str, list]) -> Params:
        url = urljoin(self.base_url, self._ticker_url)
        if isinstance(markets, list):
            params = [('markets', m.upper())
                      for m in markets]
        else:
            # str
            params = {
                'markets': markets.upper()
            }
        request_data = {
            'params': params
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _kline_request(self,
                       market: str,
                       unit: int=1,
                       count: int=200,
                       to: Union[None, datetime]=None) -> Params:
        url = urljoin(self.base_url, self._kline_url.format(unit=unit))
        request_data = {
            'params': {
                'market': market.upper(),
                'unit': unit,
                'count': count,
            }
        }
        if to is not None:
            to = to.strftime('%Y-%m-%dT%X')
            request_data['params']['to'] = to
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _trades_request(self,
                        market: str,
                        count: int=500,
                        to: Union[datetime, None]=None,
                        cursor: Union[str, None]=None) -> Params:
        url = urljoin(self.base_url, self._trades_url)
        request_data = {
            'params': {
                'market': market.upper(),
                'count': count
            }
        }
        if cursor is not None:
            request_data['params']['cursor'] = cursor
        if to is not None:
            to = to.strftime('%Y-%m-%dT%X')
            request_data['params']['to'] = to
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _depth_request(self, markets: Union[str, list]) -> Params:
        url = urljoin(self.base_url, self._depth_url)
        if isinstance(markets, list):
            params = [('markets', m.upper())
                      for m in markets]
        else:
            params = {
                'markets': markets.upper()
            }
        request_data = {
            'params': params
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )
