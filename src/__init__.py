"""
author: thomaszdxsn
"""
from .monitors import *
from .sdk import *


MONITOR_MAP = {
    'okex_future': OkexFutureMonitor,
    'okex_spot': OkexSpotMonitor,
    'huobi': HuobiMonitor,
    'bitfinex': BitfinexMonitor,
    'binance': BinanceMonitor,
    'bitflyer': BitflyerMonitor
}