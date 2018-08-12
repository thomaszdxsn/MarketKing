"""
Author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import RestSdkAbstract
from ..schemas import Params


class DigifinexRest():
    """
    doc: https://github.com/DigiFinex/api
    TODO: 这个交易所的行情数据必须要传递sign签名参数
    """
    base_url = 'https://openapi.digifinex.com/'
    _ticker_url = '/v2/ticker'
    _depth_url = '/v2/depth'
