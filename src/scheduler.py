"""
author: thomaszdxsn
"""
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

__all__ = (
    'create_scheduler',
)


def create_scheduler(event_loop=None) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=pytz.utc,
                                 event_loop=event_loop)
    return scheduler
