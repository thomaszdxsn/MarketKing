"""
author: thomaszdxsn
"""
import logging

from dynaconf import settings


LOGGING_LEVEL = settings.get('LOGGING_LEVEL', 'WARNING')
logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL)
)