"""
author: thomaszdxsn
"""
import asyncio
import logging

import uvloop
import pytest
from dynaconf import settings

from src.scheduler import create_scheduler

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


LOGGING_LEVEL = settings.get('LOGGING_LEVEL', 'WARNING')
logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL)
)

@pytest.fixture
def loop_factory():
    return uvloop.EventLoopPolicy()


@pytest.fixture
def scheduler(loop):
    yield create_scheduler(loop)
