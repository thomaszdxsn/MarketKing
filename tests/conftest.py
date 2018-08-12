"""
author: thomaszdxsn
"""
import logging

import pytest
from dynaconf import settings


from src.scheduler import create_scheduler


LOGGING_LEVEL = settings.get('LOGGING_LEVEL', 'WARNING')
logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL)
)


@pytest.fixture
def scheduler(loop):
    yield create_scheduler(loop)
