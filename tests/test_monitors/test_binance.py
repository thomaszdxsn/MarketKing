"""
author: thomaszdxsn
"""
import pytest
from dynaconf import settings

from src.monitors.binance import BinanceMonitor
from src.monitors.huobi import HuobiMonitor
from src.monitors.bitfinex import BitfinexMonitor
from src.monitors.bitflyer import BitflyerMonitor
from src.tunnels.queues import QueueTunnel
from src.storage.mongo import MongoStorage


# @pytest.mark.skip
async def test_monitor(scheduler):
    import asyncio
    pairs = settings['EXCHANGES']
    tunnel = QueueTunnel()
    monitor = BitflyerMonitor(symbols=pairs['bitflyer']['symbols'],
                              scheduler=scheduler,
                              tunnel=tunnel)
    await monitor.schedule()
    monitor = BitfinexMonitor(symbols=pairs['bitfinex']['symbols'],
                              scheduler=scheduler,
                              tunnel=tunnel)
    await monitor.schedule()
    monitor = HuobiMonitor(symbols=pairs['huobi']['symbols'],
                           scheduler=scheduler,
                           tunnel=tunnel)
    await monitor.schedule()
    monitor = BinanceMonitor(symbols=pairs['binance']['symbols'],
                           scheduler=scheduler,
                           tunnel=tunnel)
    await monitor.schedule()
    scheduler.start()
    await asyncio.sleep(15)
    print(tunnel._container.keys(), [v.qsize() for v in tunnel._container.values()])
    storage = MongoStorage()
    workers = [
        storage.worker(tunnel, id_)
        for id_ in tunnel._container.keys()
    ]
    asyncio.gather(*workers)
    while True:
        print(tunnel._container.keys())
        print([v.qsize() for v in tunnel._container.values()])
        await asyncio.sleep(5)