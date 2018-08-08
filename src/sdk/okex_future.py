"""
author: thomaszdxsn
"""
from urllib.parse import urljoin

from . import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas import Params


class OkexFutureRest(RestSdkAbstract):
    base_url = 'https://www.okex.com/'
    _ticker_url = '/api/v1/future_ticker'
    _depth_url = '/api/v1/future_depth'
    _trades_url = '/api/v1/future_trades'
    _kline_url = '/api/v1/future_kline'

    headers = {
        'ContentType': 'application/x-www-form-urlencoded'
    }

    def _ticker_request(self, symbol: str, contract_type: str) -> Params:
        request_data = {
            'params': {
                'symbol': symbol,
                'contract_type': contract_type
            },
            'headers': self.headers
        }
        url = urljoin(self.base_url, self._ticker_url)
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _depth_request(self,
                       symbol: str,
                       contract_type: str,
                       size: int=20,
                       merge: bool=True) -> Params:
        request_data = {
            'params': {
                'symbol': symbol,
                'contract_type': contract_type,
                'size': size,
                'merge': int(merge)
            },
            'headers': self.headers
        }
        url = urljoin(self.base_url, self._depth_url)
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _kline_request(self,
                       symbol: str,
                       type_: str,
                       contract_type: str,
                       size: int=0,
                       since: int=0) -> Params:
        request_data = {
            'params': {
                'symbol': symbol,
                'type': type_,
                'contract_type': contract_type,
                'size': size,
                'since': since
            },
            'headers': self.headers
        }
        url = urljoin(self.base_url, self._kline_url)
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _trades_request(self, symbol: str, contract_type: str) -> Params:
        request_data = {
            'params': {
                'symbol': symbol,
                'contract_type': contract_type
            },
            'headers': self.headers
        }
        url = urljoin(self.base_url, self._trades_url)
        return  Params(
            args=(url,),
            kwargs=request_data
        )


class OkexFutureWebsocket(WebsocketSdkAbstract):
    ws_url = 'wss://real.okex.com:10440/websocket/okexapi'

    def register_kline(self,
                       symbol: str,
                       contract_type: str,
                       type_: str='1min'):
        channel_info = {
            'event': 'addChannel',
            'channel': f'ok_sub_futureusd_{symbol}_kline_'
                       f'{contract_type}_{type_}'
        }
        self.register_channel(channel_info)

    def register_ticker(self, symbol: str, contract_type: str):
        channel_info = {
            'event': 'addChannel',
            'channel': f'ok_sub_futureusd_{symbol}_ticker_{contract_type}'
        }
        self.register_channel(channel_info)

    def register_trades(self, symbol: str, contract_type: str):
        channel_info = {
            'event': 'addChannel',
            'channel': f"ok_sub_futureusd_{symbol}_trade_{contract_type}"
        }
        self.register_channel(channel_info)

    def register_depth(self, symbol: str, contract_type: str, size: int=20):
        channel_info = {
            'event': 'addChannel',
            'channel': f"ok_sub_futureusd_{symbol}_depth_{contract_type}_{size}"
        }
        self.register_channel(channel_info)