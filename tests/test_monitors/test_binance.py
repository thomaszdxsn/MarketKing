"""
author: thomaszdxsn
"""
import pytest
from dynaconf import settings

from src.monitors.binance import BinanceMonitor
from src.monitors.huobi import HuobiMonitor
from src.monitors.bitfinex import BitfinexMonitor
from src.monitors.bitflyer import BitflyerMonitor


@pytest.mark.skip
async def test_monitor(scheduler):
    import asyncio
    pairs = settings['EXCHANGES']
    monitor = BitflyerMonitor(symbols=pairs['bitflyer']['symbols'],
                              scheduler=scheduler)
    await monitor.schedule()
    scheduler.start()
    while 1:
        print('sleep....')
        await asyncio.sleep(5)
