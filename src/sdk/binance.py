"""
author: thomaszdxsn
"""
import atexit
from urllib.parse import urljoin
from typing import Union

from . import WebsocketSdkAbstract, RestSdkAbstract
from ..schemas import Params
from ..utils import close_session

__all__ = (
    'BinanceRest',
    'BinanceWebsocket'
)


class BinanceRest(RestSdkAbstract):
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
                'symbol': symbol.upper(),
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
                'symbol': symbol.upper()
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
                'symbol': symbol.upper(),
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
                'symbol': symbol.upper(),
                'limit': limit
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )


class BinanceWebsocket(WebsocketSdkAbstract):
    """
    doc: https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md
    """
    ws_url = 'wss://stream.binance.com:9443'

    def register_trades(self, symbol: str):
        channel_info = f"{symbol.lower()}@trade"
        self.register_channel(channel_info)

    def register_kline(self, symbol: str, interval: str='1m'):
        channel_info = f"{symbol.lower()}@kline_{interval}"
        self.register_channel(channel_info)

    def register_depth(self, symbol: str, levels: int=20):
        channel_info = f"{symbol.lower()}@depth{levels}"
        self.register_channel(channel_info)

    def register_ticker(self, symbol: str):
        channel_info = f"{symbol.lower()}@ticker"
        self.register_channel(channel_info)

    def _populate_ws_url(self):
        streams = "/".join(self.register_hub)
        url = f"{self.ws_url}/stream?streams={streams}"
        return url

    async def setup_ws_client(self):
        if self.ws_url is None:
            raise ValueError('class attribute `ws_url` should not be None')
        if self.ws_client is None:
            self.ws_client = await self._session.ws_connect(
                self._populate_ws_url(),
                proxy='http://127.0.0.1:1087'
            )
            atexit.register(close_session, self._session)
        return self.ws_client

    async def subscribe(self, *args, **kwargs):
        pass