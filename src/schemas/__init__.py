"""
author: thomaszdxsn
"""
from abc import ABC
from dataclasses import asdict, dataclass


class DataClassAbstract(ABC):

    def to_dict(self, dict_factory=dict):
        return asdict(self, dict_factory=dict_factory)


@dataclass
class Params(DataClassAbstract):
    args: tuple
    kwargs: dict