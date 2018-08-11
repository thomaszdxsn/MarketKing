"""
author: thomaszdxsn
"""
import enum

__all__ = (
    'LogMsgFmt',
)


class LogMsgFmt(enum.Enum):
    HTTP_ACTION = '{method}|{url}'
    HTTP_RESPONSE = '{method}|{url}|{response}'
    EXCEPTION = '{exc.__class__.__name__}|{exc.args}'