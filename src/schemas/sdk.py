"""
author: thomaszdxsn
"""
import dataclasses
import enum
from typing import Any

from . import DataClassAbstract


class HttpErrorEnum(enum.Enum):
    NotError = 0
    ClientError = 1
    OtherError = 2


@dataclasses.dataclass
class ResponseMsg(DataClassAbstract):
    data: Any
    error: int = HttpErrorEnum.NotError.value
