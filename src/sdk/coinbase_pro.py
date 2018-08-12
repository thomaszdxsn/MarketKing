"""
author: thomaszdxsn
"""
from datetime import datetime
from urllib.parse import urljoin
from typing import Union

from aiohttp import ClientTimeout

from . import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas import Params


class CoinbaseProRest(RestSdkAbstract):
    """
    doc: https://docs.pro.coinbase.com/#get-product-order-book
    """
    base_url = 'https://api.pro.coinbase.com'
    _depth_url = '/products/{product_id}/book'
    _ticker_url = '/products/{product_id}/ticker'
    _trades_url = '/products/{product_id}/trades'
    _kline_url = '/products/{product_id}/candles'

    def _depth_request(self, product_id: str, level: int=2) -> Params:
        url = urljoin(self.base_url,
                      self._depth_url.format(product_id=product_id.upper()))
        request_data = {
            'params': {
                'level': level
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _ticker_request(self, product_id: str) -> Params:
        url = urljoin(self.base_url,
                      self._ticker_url.format(product_id=product_id))
        return Params(
            args=(url,)
        )

    def _trades_request(self, product_id: str) -> Params:
        url = urljoin(self.base_url,
                      self._trades_url.format(product_id=product_id))
        return Params(
            args=(url,)
        )

    def _kline_request(self,
                       product_id: str,
                       granularity: int=60,
                       start: Union[datetime, None]=None,
                       end: Union[datetime, None]=None) -> Params:
        url = urljoin(self.base_url,
                      self._kline_url.format(product_id=product_id))
        request_data = {
            'params': {
                'granularity': granularity
            }
        }
        if start is not None:
            request_data['params']['start'] = start.replace(
                microsecond=0
            ).isoformat()
        if end is not None:
            request_data['params']['end'] = end.replace(
                microsecond=0
            ).isoformat()
        return Params(
            args=(url,),
            kwargs=request_data
        )


class CoinbaseProWebsocket(WebsocketSdkAbstract):
    _request_read_timeout: float = 60
    _request_conn_timeout: float = 20.0

    ws_url = 'wss://ws-feed.pro.coinbase.com'

    async def subscribe(self, *args, **kwargs):
        sub_msg = {
            'type': 'subscribe',
            'channels': self.register_hub
        }
        await self.ws_client.send_json(sub_msg)

    def register_ticker(self, product_id: str):
        channel_info = {
            'name': 'ticker',
            'product_ids': [product_id]
        }
        self.register_channel(channel_info)

    def register_depth(self, product_id: str):
        channel_info = {
            'name': 'level2',
            'product_ids': [product_id]
        }
        self.register_channel(channel_info)