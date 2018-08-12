"""
author: thomaszdxsn
"""
from datetime import datetime

__all__ = (
    'factory_utcnow',
)


def factory_utcnow():
    return datetime.utcnow()