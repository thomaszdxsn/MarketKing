"""
author: thomaszdxsn
"""
import asyncio
import arrow
import logging
from scripts.mongo2s3 import main

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()
start, end = arrow.utcnow().shift(weeks=-1), arrow.utcnow().shift(days=-1)
loop.run_until_complete(main(start, end))


