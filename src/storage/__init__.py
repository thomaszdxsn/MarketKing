"""
author: thomaszdxsn
"""
from abc import ABC, abstractmethod
import logging

from ..tunnels import TunnelAbstract



class StorageAbstract(ABC):

    def __init__(self):
        self.logger = logging.getLogger(f'storage.{self.__class__.__name__}')

    @abstractmethod
    async def worker(self, tunnel: TunnelAbstract, id_: str):
        pass


from .mongo import MongoStorage