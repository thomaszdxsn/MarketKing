"""
Author: thomaszdxsn
"""
from urllib.parse import urljoin

from . import RestSdkAbstract
from ..schemas import Params

__all__ = (
    'BithumpRest',
)


class BithumpRest(RestSdkAbstract):
    """
    doc: https://www.bithumb.com/u1/US127
    """
    base_url = 'https://api.bithumb.com/'
    _ticker_url = '/public/ticker/{currency}'
    _depth_url = '/public/orderbook/{currency}'
    _trades_url = '/public/transaction_history/{currency}'

    def _ticker_request(self, currency: str) -> Params:
        url = urljoin(
            self.base_url,
            self._ticker_url.format(currency=currency)
        )
        return Params(args=(url,))

    def _depth_request(self, currency: str) -> Params:
        url = urljoin(
            self.base_url,
            self._depth_url.format(currency=currency)
        )
        return Params(args=(url,))
    
    def _trades_request(self, currency: str) -> Params:
        url = urljoin(
            self.base_url,
            self._trades_url.format(currency=currency)
        )
        return Params(args=(url,))