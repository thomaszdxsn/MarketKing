"""
author: thomaszdxsn
"""
import collections
from asyncio.queues import Queue
from typing import Tuple

from . import TunnelAbstract
from ..schemas.items import ExchangeItem

__all__ = ('QueueTunnel',)


class QueueTunnel(TunnelAbstract):
    # TODO: 做成异步迭代器的形式

    def __init__(self, maxsize=0, loop=None):
        def queue_factory():
            return Queue(maxsize=maxsize, loop=loop)
        self._container = collections.defaultdict(queue_factory)

    def __len__(self):
        return len(self._container)

    def keys(self):
        return list(self._container.keys())

    def get_queue(self, item_id):
        return self._container[item_id]

    def put(self, item: ExchangeItem):
        queue = self.get_queue(item.id)
        queue.put_nowait(item)

    async def put_async(self, item: ExchangeItem):
        queue = self.get_queue(item.id)
        await queue.put(item)

    async def get_async(self, id_: str) -> ExchangeItem:
        queue = self.get_queue(id_)
        item = await queue.get()
        queue.task_done()
        return item

    def get(self, id_: str) -> ExchangeItem:
        queue = self.get_queue(id_)
        item = queue.get_nowait()
        queue.task_done()
        return item