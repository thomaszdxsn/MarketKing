"""
author: thomaszdxsn
"""
import pytest
from dynaconf import settings

from src.monitors.okex_future import OkexFutureMonitor


async def test_monitor(scheduler):
    import asyncio
    pairs = settings['EXCHANGES']
    monitor = OkexFutureMonitor(symbols=pairs['okex_future']['all'],
                                scheduler=scheduler)
    await monitor.schedule()
    scheduler.start()
    while 1:
        print('sleep....')
        await asyncio.sleep(5)