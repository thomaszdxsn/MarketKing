"""
Author: thomaszdxsn
"""
import asyncio
from datetime import datetime, timedelta
from urllib.parse import urljoin
from typing import Union

from . import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas import Params

__all__ = (
    'LBankRest',
    'LBankWebsocket'
)


class LBankRest(RestSdkAbstract):
    """
    doc: https://github.com/LBank-exchange/lbank-official-api-docs/tree/master/API-For-Spot-CN
    """
    base_url = 'http://api.lbank.info/'
    _ticker_url = '/v1/ticker.do'
    _depth_url = '/v1/depth.do'
    _trades_url = '/v1/trades.do'
    _kline_url = '/v1/kline.do'

    _headers = {
        'ContentType': 'application/x-www-form-urlencoded'
    }

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

    def _depth_request(self, 
                       symbol: str,
                       size: int=60,
                       merge: int=0) -> Params:
        url = urljoin(self.base_url, self._depth_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'size': size,
                'merge': merge
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _trades_request(self,
                        symbol: str,
                        size: int=600,
                        time: Union[int, None]=None) -> Params:
        url = urljoin(self.base_url, self._trades_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'size': size
            }
        }
        if time is not None:
            request_data['params']['time'] = time
        return Params(
            args=(url,),
            kwargs=request_data
        )
    
    def _kline_request(self,
                       symbol: str,
                       size: int=60,
                       type_: str='minute1',
                       time: Union[int, None]=None) -> Params:
        if time is None:
            time = int((datetime.now() - timedelta(hours=1)).timestamp())
        url = urljoin(self.base_url, self._kline_url)
        request_data = {
            'params': {
                'symbol': symbol,
                'size': size,
                'type': type_,
                'time': time
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    
class LBankWebsocket(WebsocketSdkAbstract):
    ws_url = 'ws://api.lbank.info/ws/V2/'

    def register_depth(self, symbol: str, size: int=10):
        channel_info = {
            'action': 'subscribe',
            'subscribe': 'depth',
            'depth': size,
            'pair': symbol
        }
        self.register_channel(channel_info)

    def register_ticker(self, symbol: str):
        channel_info = {
            'action': 'subscribe',
            'subscribe': 'tick',
            'pair': symbol
        }
        self.register_channel(channel_info)

    def register_trades(self, symbol: str):
        channel_info = {
            'action': 'subscribe',
            'subscribe': 'trade',
            'pair': symbol
        }
        self.register_channel(channel_info)

    def register_kline(self, symbol: str, type_: str='1min'):
        channel_info = {
            'action': 'subscribe',
            'subscribe': 'kbar',
            'kbar': type_,
            'pair': symbol
        }
        self.register_channel(channel_info)

    async def subscribe(self, *args, **kwargs):
        if not self.ws_client:
            await self.setup_ws_client()
        for channel_info in self.register_hub:
            await self.ws_client.send_json(channel_info)
            await asyncio.sleep(.2)