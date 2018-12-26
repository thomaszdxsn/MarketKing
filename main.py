"""
author: thomaszdxsn
"""
import asyncio
import math

import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from dynaconf import settings

from src import MONITOR_MAP
from src.scheduler import create_scheduler
from src.tunnels import QueueTunnel
from src.storage import MongoStorage
from src.utils import chunk


class Main(object):

    def __init__(self, exchange_info):
        self.scheduler = create_scheduler()
        self.tunnel = QueueTunnel()
        self.storage = MongoStorage(settings.MONGO_URI,
                                    settings.as_int('MONGO_POOL_SIZE'))
        self.exchanges_settings: dict = exchange_info
        self._worked_tunnel = set()

    async def supervisor(self):
        """定时任务，如果tunnel出现新的key，就为它apawn一个worker"""
        for key in self.tunnel.keys():
            if key not in self._worked_tunnel:
                self._worked_tunnel.add(key)
                if key.endswith('depth'):
                    worker_num = 6
                else:
                    worker_num = 3
                for i in range(worker_num):
                    # 开启两个worker
                    self.scheduler.run_later(
                        self.storage.worker,
                        args=(self.tunnel, key)
                    )

    async def schedule_monitors(self):
        for exchange, info in self.exchanges_settings:
            monitor_class = MONITOR_MAP[exchange]
            monitor = monitor_class(symbols=info['symbols'],
                                    scheduler=self.scheduler,
                                    tunnel=self.tunnel)
            try:
                await monitor.schedule()
            except:
                await asyncio.sleep(5)

    async def main(self):
        self.scheduler.start()
        self.scheduler.add_job(self.supervisor, trigger='cron', minute='*')
        await self.schedule_monitors()
        # while True:
        #     for k, v in self.tunnel._container.items():
        #         print(f'{k}: {v.qsize()}')
        #     print(f'{len(self.tunnel.keys())} workers: {len(self._worked_tunnel)}')
        #     await asyncio.sleep(5)


def main(exchange_info):
    try:
        import logging
        logging.basicConfig(level=logging.WARNING)
        loop = asyncio.get_event_loop()
        m = Main(exchange_info)
        loop.run_until_complete(m.main())
        loop.run_forever()
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    import os
    import aioprocessing
    processes = []
    chunk_num = len(settings['EXCHANGES']) //  os.cpu_count()
    for exchange_info in chunk(settings['EXCHANGES'].items(), chunk_num):
        p = aioprocessing.AioProcess(target=main, args=(exchange_info,))
        processes.append(p)
    [p.start() for p in processes]

