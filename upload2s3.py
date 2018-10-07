"""
author: thomaszdxsn
"""
import asyncio
import logging

import arrow
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler

from scripts.mongo2s3 import main

logging.basicConfig(level=logging.INFO)


def task():
    loop = asyncio.get_event_loop()
    start, end = arrow.utcnow().shift(weeks=-1), arrow.utcnow()
    loop.run_until_complete(main(start, end))


scheduler = BlockingScheduler(timezone=pytz.UTC)
scheduler.add_job(task, trigger='cron', hour=0, minute=15)
print('starting scheduler')
scheduler.start()


