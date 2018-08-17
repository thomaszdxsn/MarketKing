"""
author: thomaszdxsn
"""
from abc import ABC, abstractmethod

from ..schemas.items import Item


class TunnelAbstract(ABC):
    """
    数据中转站|管道
    """

    @abstractmethod
    def put(self, item: Item):
        pass

    @abstractmethod
    async def put_async(self, item: Item):
        pass

    @abstractmethod
    def get(self, *args):
        pass

    @abstractmethod
    async def get_async(self, *args):
        pass