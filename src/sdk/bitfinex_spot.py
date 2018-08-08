"""
author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import WebsocketSdkAbstract, RestSdkAbstract
from ..schemas import Params


class BitfinexRest(RestSdkAbstract):
    """API version: 2.0
    doc: https://bitfinex.readme.io/v2/reference#rest-public-ticker
    """
    base_url = 'https://api.bitfinex.com/'
    _ticker_url = '/v2/ticker/{symbol}'
    _kline_url = '/v2/candles/trade:{time_frame}:{symbol}/{section}'
    _trades_url = '/v2/trades/{symbol}/hist'
    _depth_url = '/v2/book/{symbol}/{precision}'

    def _ticker_request(self, symbol: str) -> Params:
        url = urljoin(
            self.base_url,
            self._ticker_url.format(symbol=f't{symbol.upper()}')
        )
        return Params(
            args=(url,),
        )

    def _kline_request(self,
                       symbol: str,
                       time_frame: str='1m',
                       section: str='hist',
                       limit: int=100,
                       start: Union[int, None]=None,
                       end: Union[int, None]=None,
                       sort: int=-1) -> Params:
        assert section in ('hist', 'last'), 'section must be one ' \
                                            'of last or hist'
        url = urljoin(
            self.base_url,
            self._kline_url.format(
                time_frame=time_frame,
                symbol=f't{symbol.upper()}',
                section=section
            )
        )

        request_data = {
            'params': {
                'limit': limit,
                'sort': sort
            }
        }
        if start is not None:
            request_data['params']['start'] = start
        if end is not None:
            request_data['params']['start'] = end
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _trades_request(self,
                        symbol: str,
                        limit: int=100,
                        start: Union[int, None]=None,
                        end: Union[int, None]=None,
                        sort: int=-1) -> Params:
        url = urljoin(
            self.base_url,
            self._trades_url.format(
                symbol=f't{symbol.upper()}'
            )
        )
        request_data = {
            'params': {
                'limit': limit,
                'sort': sort
            }
        }
        if start is not None:
            request_data['params']['start'] = start
        if end is not None:
            request_data['params']['start'] = end
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _depth_request(self,
                       symbol: str,
                       precision: str='P0',
                       len_: int=25) -> Params:
        url = urljoin(
            self.base_url,
            self._depth_url.format(
                symbol=f't{symbol.upper()}',
                precision=precision
            )
        )
        request_data = {
            'params': {
                'len': len_
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )


class BitfinexWebsocket(WebsocketSdkAbstract):
    ws_url = 'wss://api.bitfinex.com/ws/2'

    def register_ticker(self, symbol: str):
        channel_info = {
            'event': 'subscribe',
            'channel': 'ticker',
            'symbol': f't{symbol.upper()}'
        }
        self.register_channel(channel_info)

    def register_trades(self, symbol: str):
        channel_info = {
            'event': 'subscribe',
            'channel': 'trades',
            'symbol': f"t{symbol.upper()}"
        }
        self.register_channel(channel_info)

    def register_kline(self, symbol: str, time_frame: str='1m'):
        channel_info = {
            'event': 'subscribe',
            'channel': 'candles',
            'key': f'trade:{time_frame}:t{symbol.upper()}'
        }
        self.register_channel(channel_info)

    def register_depth(self,
                       symbol: str,
                       precision: str='P0',
                       frequency: str='F0',
                       length: int=25):
        """
        doc: https://bitfinex.readme.io/v2/reference#ws-public-order-books
        """
        channel_info = {
            'event': 'subscribe',
            'channel': 'book',
            'symbol': f"t{symbol.upper()}",
            'precision': precision,
            'frequency': frequency,
            'length': length
        }
        self.register_channel(channel_info)
