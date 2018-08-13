"""
author: thomaszdxsn
"""
from .monitors import *
from .sdk import *


EXCHANGE_MAP = {
    'okex_future': {
        'monitor': OkexFutureMonitor,
        'rest_sdk': OkexFutureRest,
        'ws_sdk': OkexFutureWebsocket,
    },
    'okex_spot': {
        'monitor': OkexSpotMonitor,
        'rest_sdk': OkexSpotRest,
        'ws_sdk': OkexSpotWebsocket,
    },
    'binance': {
        'monitor': BinanceMonitor,
        'rest_sdk': BinanceRest,
        'ws_sdk': BinanceWebsocket
    }
}