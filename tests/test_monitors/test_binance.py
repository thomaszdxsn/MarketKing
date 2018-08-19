"""
author: thomaszdxsn
"""
import pytest
from dynaconf import settings

from src.monitors.binance import BinanceMonitor
from src.monitors.huobi import HuobiMonitor
from src.monitors.bitfinex import BitfinexMonitor
from src.monitors.bitflyer import BitflyerMonitor
from src.monitors import BitmexMonitor, HitBTCMonitor
from src.tunnels.queues import QueueTunnel
from src.storage.mongo import MongoStorage



# @pytest.mark.skip
async def test_monitor(scheduler):
    import asyncio
    pairs = settings['EXCHANGES']['hitbtc']['symbols']
    tunnel = QueueTunnel()
    monitor = HitBTCMonitor(symbols=pairs,
                            scheduler=scheduler,
                            tunnel=tunnel)
    await monitor.schedule()
    scheduler.start()
    while True:
        # print(tunnel._container.keys())
        # print([v.qsize() for v in tunnel._container.values()])
        await asyncio.sleep(5)