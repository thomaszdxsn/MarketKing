"""
author: thomaszdxsn
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from . import add_slots, DataClassAbstract


__all__ = ('ExchangeItem', 'Item')


class Item(ABC):
    pass

    @abstractmethod
    def id(self):
        pass


@add_slots
@dataclass
class ExchangeItem(Item):
    exchange: str
    data_type: str
    data: DataClassAbstract

    @property
    def id(self):
        return f"{self.exchange}|{self.data_type}"
