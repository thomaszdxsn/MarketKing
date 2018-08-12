"""
Author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import RestSdkAbstract
from ..schemas import Params

__all__ = (
    'BiboxRest',
)


class BiboxRest(RestSdkAbstract):
    """
    doc: https://github.com/Biboxcom/api_reference/wiki/home_zh
    """
    _base_url = 'https://api.bibox.com'
    base_url = urljoin(_base_url, '/v1/mdata')

    def _kline_request(self, 
                       pair: str,
                       period: str='1min',
                       size: int=60) -> Params:
        request_data = {
            'params': {
                'cmd': 'kline',
                'pair': pair.upper(),
                'period': period,
                'size': size
            }
        }
        return Params(
            args=(self.base_url,),
            kwargs=request_data
        )

    def _ticker_request(self, pair:str='all') -> Params:
        request_data = {
            "params": {
                'cmd': 'ticker',
                'pair': pair.upper()
            }
        }
        return Params(
            args=(self.base_url,),
            kwargs=request_data
        )

    def _depth_request(self, pair: str, size: int=20) -> Params:
        assert 1 <= size <= 200, 'size must be one of range 1-200'
        request_data = {
            'params': {
                'pair': pair.upper(),
                'size': size,
                'cmd': 'depth'
            }
        }
        return Params(
            args=(self.base_url,),
            kwargs=request_data
        )

    def _trades_request(self, pair: str, size: int=200) -> Params:
        assert 1 <= size <= 200, 'size must be one of range 1-200'
        request_data = {
            'params': {
                'pair': pair.upper(),
                'size': size,
                'cmd': 'deals'
            }
        }
        return Params(
            args=(self.base_url,),
            kwargs=request_data
        )