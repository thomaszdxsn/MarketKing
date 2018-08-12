"""
author: thomaszdxsn
"""
import pytest
from dynaconf import settings

from src.monitors.okex_spot import OkexSpotMonitor


@pytest.mark.manual
async def test_monitor(scheduler):
    import asyncio
    pairs = settings['EXCHANGES']
    print(pairs)
    monitor = OkexSpotMonitor(symbols=pairs['okex_spot']['all'],
                              scheduler=scheduler)
    await monitor.schedule()
    scheduler.start()
    while 1:
        print('sleep....')
        await asyncio.sleep(5)

