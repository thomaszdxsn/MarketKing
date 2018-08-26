"""
author: thomaszdxsn
"""
from datetime import datetime
from dataclasses import dataclass

from . import DataClassAbstract

__all__ = (
    'S3Record',
)


@dataclass
class S3Record(DataClassAbstract):
    collection: str
    pair: str
    date: datetime
    is_export: bool=False
    is_upload: bool=False
    size: int=None
    local_file: str=None
    s3_key: str=None
    presign_url: str=None