"""
author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas import Params

__all__ = (
    'ZBRest',
    'ZBWebsocket'
)


class ZBRest(RestSdkAbstract):
    """
    doc: https://www.zb.com/i/developer
    """
    base_url = 'http://api.zb.cn/'
    _ticker_url = 'data/v1/ticker'
    _depth_url = '/data/v1/depth'
    _trades_url = '/data/v1/trades'
    _kline_url = '/data/v1/kline'

    def _ticker_request(self, market: str) -> Params:
        url = urljoin(self.base_url, self._ticker_url)
        request_data = {
            'params': {
                'market': market
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _depth_request(self, 
                       market: str, 
                       size: int=20, 
                       merge: Union[float, None]=None) -> Params:
        url = urljoin(self.base_url, self._depth_url)
        request_data = {
            'params': {
                'market': market,
                'size': size
            }
        }
        if merge is not None:
            request_data['params']['merge'] = merge
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _trades_request(self,
                        market: str,
                        since: Union[int, None]=None) -> Params:
        url = urljoin(self.base_url, self._trades_url)
        request_data = {
            'params': {
                'market': market
            }
        }
        if since is not None:
            request_data['params']['since'] = since
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _kline_request(self,
                       market: str,
                       type_: str='1min',
                       since: Union[int, None]=None,
                       size: int=1000) -> Params:
        url = urljoin(self.base_url, self._kline_url)
        request_data = {
            'params': {
                'market': market,
                'type': type_,
                'size': size
            }
        }
        if since is not None:
            request_data['params']['since'] = since
        return Params(
            args=(url,),
            kwargs=request_data
        )
        

class ZBWebsocket(WebsocketSdkAbstract):
    ws_url = 'wss://api.zb.cn:9999/websocket'

    def register_ticker(self, symbol: str):
        channel_info = {
            'event': 'addChannel',
            'channel': f'{symbol}_ticker'
        }
        self.register_channel(channel_info)

    def register_depth(self, symbol: str):
        channel_info = {
            'event': 'addChannel',
            'channel': f'{symbol}_depth'
        }
        self.register_channel(channel_info) 

    def register_trades(self, symbol: str):
        channel_info = {
            'event': 'addChannel',
            'channel': f'{symbol}_trades'
        }
        self.register_channel(channel_info)