"""
Author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import RestSdkAbstract
from ..schemas import Params

__all__ = (
    'BithumbRest',
)


class BithumbRest(RestSdkAbstract):
    """
    doc: https://www.bithumb.com/u1/US127
    """
    base_url = 'https://api.bithumb.com/'
    _ticker_url = '/public/ticker/{currency}'
    _depth_url = '/public/orderbook/{currency}'
    _trades_url = '/public/transaction_history/{currency}'

    def _ticker_request(self, currency: str='ALL') -> Params:
        url = urljoin(
            self.base_url,
            self._ticker_url.format(currency=currency)
        )
        return Params(args=(url,))

    def _depth_request(self,
                       currency: str='ALL',
                       group_orders: int=1,
                       count: int=5) -> Params:
        url = urljoin(
            self.base_url,
            self._depth_url.format(currency=currency)
        )
        request_data = {
            'params': {
                'group_orders': group_orders,
                'count': count
            }
        }
        return Params(args=(url,), kwargs=request_data)
    
    def _trades_request(self,
                        currency: str,
                        cont_no: Union[int,None]=None,
                        count: int=200) -> Params:
        url = urljoin(
            self.base_url,
            self._trades_url.format(currency=currency)
        )
        return Params(args=(url,))