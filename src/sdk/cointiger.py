"""
Author: thomaszdxsn
"""
import json
import gzip
from urllib.parse import urljoin

from . import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas import Params

__all__ = (
    'CointigerRest',
    'CointigerWebsocket'
)


class CointigerRest(RestSdkAbstract):
    """
    doc: https://github.com/cointiger/api-docs/wiki
    """
    base_url = 'https://api.cointiger.pro/'
    _ticker_url = '/exchange/trading/api/market/detail'
    _depth_url = '/exchange/trading/api/market/depth'
    _trades_url = '/exchange/trading/api/market/history/trade'
    _kline_url = '/exchange/trading/api/market/history/kline'

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
    
    def _trades_request(self, symbol: str, size: int=2000) -> Params:
        url = urljoin(self.base_url, self._trades_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'size': size
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        ) 

    def _depth_request(self, symbol: str, type_: str='step0') -> Params:
        url = urljoin(self.base_url, self._depth_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'type': type_
            } 
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _kline_request(self, 
                       symbol: str,
                       period: str='1min',
                       size: int=60) -> Params:
        url = urljoin(self.base_url, self._kline_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'period': period,
                'size': size
            } 
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )



class CointigerWebsocket(WebsocketSdkAbstract):
    ws_url = 'wss://api.cointiger.pro/exchange-market/ws'

    def register_kline(self, 
                       symbol:str, 
                       period: str='1min', 
                       cb_id: int=1):
        channel_info = {
            'event': 'sub',
            'params': {
                'channel': f'market_{symbol}_kline_{period}',
                'cb_id': cb_id
            }
        }
        self.register_channel(channel_info)

    def register_depth(self,
                       symbol: str,
                       type_: str='step0',
                       asks_size: int=20,
                       bids_size: int=20,
                       cb_id: int=1):
        channel_info = {
            'event': 'sub',
            'params': {
                'channel': f'market_{symbol}_depth_{type_}',
                'cb_id': cb_id,
                'asks': asks_size,
                'bids': bids_size
            }
        }
        self.register_channel(channel_info)

    def register_ticker(self, symbol: str, cb_id: int=1):
        channel_info = {
            'event': 'sub',
            'params': {
                'channel': f'market_{symbol}_ticker',
                'cb_id': cb_id
            }
        }
        self.register_channel(channel_info)

    def register_trades(self, symbol: str, cb_id: int=1):
        channel_info = {
            'event': 'sub',
            'params': {
                'channel': f'market_{symbol}_trade_ticker',
                'cb_id': cb_id
            }
        }
        self.register_channel(channel_info)

    async def connect(self, handler: Callable):
         async for msg in self.ws_client:
             raw_data = gzip.decompress(msg.data)
             data = json.loads(raw_data, encoding='ascii')
             ping = data.get('ping')
             if ping:
                 await self.ws_client.send_json({
                     'pong': ping
                 })
                 continue
             handler(data)