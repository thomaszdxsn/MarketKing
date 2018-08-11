"""
Author: thomaszdxsn
"""
from urllib.parse import urljoin

from . import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas import Params

__all__ = (
    'BittrexRest',
)


class BittrexRest(RestSdkAbstract):
    """
    doc: https://support.bittrex.com/hc/en-us/articles/115003723911
    """
    base_url = 'https://bittrex.com/'
    _ticker_url = '/api/v1.1/public/getmarketsummary'
    _depth_url = '/api/v1.1/public/getorderbook'
    _trades_url = '/api/v1.1/public/getmarkethistory'

    def _ticker_request(self, market: str) -> Params:
        url = urljoin(self.base_url, self._ticker_url)
        request_data = {
            'params': {
                'market': market.upper()
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _depth_request(self, market: str, type_: str='both') -> Params:
        url = urljoin(self.base_url, self._depth_url)
        request_data = {
            'params': {
                'market': market.upper(),
                'type': type_
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )
    
    def _trades_request(self, market: str) -> Params:
        url = urljoin(self.base_url, self._trades_url)
        request_data = {
            'params': {
                'market': market.upper()
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        ) 


class BittrexWebsocket(WebsocketSdkAbstract):
    """
    doc: https://github.com/Bittrex/bittrex.github.io

    TODO: 这不是标准的websockets, 而是另一个类ws的协议signalr。
          出于时间成本，暂时不开发这个
    """
    ws_url = 'https://socket.bittrex.com/signalr'