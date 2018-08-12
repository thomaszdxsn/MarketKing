"""
Author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import RestSdkAbstract
from ..schemas import Params

__all__ = (
    'KrakenRest',
)


class KrakenRest(RestSdkAbstract):
    """
    doc: https://www.kraken.com/help/api#get-ticker-info
    """
    base_url = 'https://api.kraken.com/'
    _ticker_url = '/0/public/Ticker'
    _kline_url = '/0/public/OHLC'
    _trades_url = '/0/public/Trades'
    _depth_url = '/0/public/Depth'

    def _ticker_request(self, pair: Union[str, list]) -> Params:
        url = urljoin(self.base_url, self._ticker_url)
        request_data = {
            'params': {
                'pair': pair if isinstance(pair, str) else ','.join(pair)
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _kline_request(self, 
                       pair: str,
                       interval: int=1,
                       since: Union[str, None]=None) -> Params:
        url = urljoin(self.base_url, self._kline_url)
        request_data = {
            'params': {
                'pair': pair,
                'interval': interval
            }
        }
        if since is not None:
            request_data['params']['since'] = since
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _depth_request(self, 
                       pair: str,
                       count: int=20) -> Params:
        url = urljoin(self.base_url, self._depth_url)
        request_data = {
            'params': {
                'pair': pair,
                'count':count
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _trades_request(self,
                        pair: str,
                        since: Union[str, None]=None) -> Params:
        url = urljoin(self.base_url, self._trades_url)
        request_data = {
            'params': {
                'pair': pair
            }
        }
        if since is not None:
            request_data['params']['since'] = since
        return Params(
            args=(url,),
            kwargs=request_data
        )
