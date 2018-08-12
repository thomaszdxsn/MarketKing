"""
author: thomaszdxsn
"""
from urllib.parse import urljoin

from . import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas import Params

__all__ = (
    'BitstampRest',
)


class BitstampRest(RestSdkAbstract):
    """
    doc: https://www.bitstamp.net/api/
    """
    base_url = 'https://www.bitstamp.net/'
    _ticker_url = '/api/v2/ticker/{currency_pair}/'
    _trades_url = '/api/v2/transactions/{currency_pair}/'
    _depth_url = '/api/v2/order_book/{currency_pair}/'

    def _ticker_request(self, currency_pair: str) -> Params:
        url = urljoin(
            self.base_url,
            self._ticker_url.format(currency_pair=currency_pair)
        )
        return Params(args=(url,))

    def _depth_request(self, currency_pair: str, group: int=0) -> Params:
        url = urljoin(
            self.base_url,
            self._depth_url.format(currency_pair=currency_pair)
        )
        request_data = {
            'params': {
                'group': group
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )

    def _trades_request(self, currency_pair: str, time: str='hour'):
        url = urljoin(
            self.base_url,
            self._trades_url.format(currency_pair=currency_pair)
        )
        request_data = {
            'params': {
                'time': time
            }
        }
        return Params(
            args=(url,),
            kwargs=request_data
        )


class BitstampWebsocket(WebsocketSdkAbstract):
    """
    TODO: 因为使用了pusher协议而不是标准的websocket，暂时不开发
    """
