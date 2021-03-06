"""
author: thomaszdxsn
"""
import random
from types import MethodType
from typing import Union, Callable

import arrow
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

__all__ = (
    'create_scheduler',
)


def run_later(self,
               func: Callable,
               args: Union[None, tuple] = None,
               kwargs: Union[None, dict] = None,
               sec: int = 5):
    """run task in {sec} seconds"""
    self.add_job(
        func,
        args=args,
        kwargs=kwargs,
        max_instances=10,
        misfire_grace_time=15 * 60
    )


def create_scheduler(event_loop=None) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=pytz.utc,
                                 event_loop=event_loop)
    scheduler.run_later = MethodType(run_later, scheduler)
    return scheduler
