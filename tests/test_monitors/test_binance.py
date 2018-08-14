"""
author: thomaszdxsn
"""
import pytest
from dynaconf import settings

from src.monitors.binance import BinanceMonitor


# @pytest.mark.skip
async def test_monitor(scheduler):
    import asyncio
    pairs = settings['EXCHANGES']
    monitor = BinanceMonitor(symbols=pairs['binance']['symbols'],
                             scheduler=scheduler)
    await monitor.schedule()
    scheduler.start()
    while 1:
        print('sleep....')
        await asyncio.sleep(5)
