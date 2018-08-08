"""
author: thomaszdxsn
"""
import dataclasses
import enum
from typing import Any

from . import DataClassAbstract


class HttpErrorEnum(enum.Enum):
    ClientError = 0
    OtherError = 1


@dataclasses.dataclass
class ResponseMsg(DataClassAbstract):
    data: Any
    error: int = HttpErrorEnum.ClientError.value
