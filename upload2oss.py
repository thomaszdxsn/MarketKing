"""
author: thomaszdxsn
"""
import asyncio
import logging

import arrow
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scripts.mongo2oss import main

logging.basicConfig(level=logging.INFO)


async def task():
    start, end = arrow.utcnow().shift(weeks=-1), arrow.utcnow().shift(days=-1)
    await main(start, end)


# scheduler = AsyncIOScheduler(timezone=pytz.UTC)
# scheduler.add_job(task, trigger='cron', hour=0, minute=15)
# print('starting scheduler')
# scheduler.start()
asyncio.get_event_loop().run_until_complete(task())