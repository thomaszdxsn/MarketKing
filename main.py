"""
author: thomaszdxsn
"""
import asyncio

import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from dynaconf import settings

from src import MONITOR_MAP
from src.scheduler import create_scheduler
from src.tunnels import QueueTunnel
from src.storage import MongoStorage


class Main(object):

    def __init__(self):
        self.scheduler = create_scheduler()
        self.tunnel = QueueTunnel()
        self.storage = MongoStorage()
        self.exchanges_settings: dict = settings['EXCHANGES']
        self._worked_tunnel = set()
        self._worker_num = 0


    async def supervisor(self):
        """定时任务，如果tunnel出现新的key，就为它apawn一个worker"""
        for key in self.tunnel.keys():
            if key not in self._worked_tunnel:
                self._worked_tunnel.add(key)
                if key.endswith('depth'):
                    worker_num = 4
                else:
                    worker_num = 2
                for i in range(worker_num):
                    # 开启两个worker
                    self.scheduler.run_later(
                        self.storage.worker,
                        args=(self.tunnel, key)
                    )
                    self._worker_num += 1

    async def schedule_monitors(self):
        for exchange, info in self.exchanges_settings.items():
            monitor_class = MONITOR_MAP[exchange]
            monitor = monitor_class(symbols=info['symbols'],
                                    scheduler=self.scheduler,
                                    tunnel=self.tunnel)
            await monitor.schedule()

    async def main(self):
        self.scheduler.start()
        self.scheduler.add_job(self.supervisor, trigger='cron', minute='*')
        await self.schedule_monitors()
        while True:
            for k, v in self.tunnel._container.items():
                print(f'{k}: {v.qsize()}')
            print(f'{len(self.tunnel.keys())} workers: {len(self._worked_tunnel)}, {self._worker_num}')
            await asyncio.sleep(5)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.WARNING)
    loop = asyncio.get_event_loop()
    m = Main()
    loop.run_until_complete(m.main())
    loop.run_forever()
