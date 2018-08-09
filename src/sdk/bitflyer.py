"""
Author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import WebsocketSdkAbstract, RestSdkAbstract
from ..schemas import Params

__all__ = (
    'BitflyerRest',
    'BitflyerWebsocket'
)


class BitflyerRest(RestSdkAbstract):
    """
    doc: https://lightning.bitflyer.com/docs?lang=zh-CN
    """
    base_url = 'https://api.bitflyer.jp/'
    _ticker_url = '/v1/ticker'
    _depth_url = '/v1/board'
    _trades_url = '/v1/executions'

    def _ticker_request(self, product_code: str) -> Params:
        url = urljoin(self.base_url, self._ticker_url)
        request_data = {
            'params': {
                'product_code': product_code.upper()
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _depth_request(self, product_code: str) -> Params:
        url = urljoin(self.base_url, self._depth_url)
        request_data = {
            'params': {
                'product_code': product_code.upper()
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _trades_request(self, 
                        product_code: str,
                        count: int=100,
                        before: Union[int, None]=None,
                        after: Union[int, None]=None):
        url = urljoin(self.base_url, self._trades_url)
        request_data = {
            'params': {
                'product_code': product_code.upper(),
                'count': count
            }
        }
        if before is not None:
            request_data['params']['before'] = before
        if after is not None:
            request_data['params']['after'] = after
        return Params(
            args=(url,),
            kwargs=request_data
        )


class BitflyerWebsocket(WebsocketSdkAbstract):
    ws_url = 'wss://ws.lightstream.bitflyer.com/json-rpc'
    
    def register_depth(self, product_code: str):
        channel_info = {
            'method': 'subscribe',
            'params': {
                'channel': f'lightning_board_snapshot_{product_code.upper()}'
            },
            'id': '1'
        }
        self.register_channel(channel_info)

    def register_ticker(self, product_code: str):
        channel_info = {
            'method': 'subscribe',
            'params': {
                'channel': f'lightning_ticker_{product_code.upper()}'
            },
            'id': '1'
        }
        self.register_channel(channel_info)

    def register_trades(self, product_code: str):
        channel_info = {
            'method': 'subscribe',
            'params': {
                'channel': f'lightning_executions_{product_code.upper()}'
            },
            'id': '1'
        }
        self.register_channel(channel_info)