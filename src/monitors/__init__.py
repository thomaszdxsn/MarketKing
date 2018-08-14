"""
author: thomaszdxsn
"""
import asyncio
import logging
from asyncio import AbstractEventLoop
from abc import ABC, abstractmethod
from typing import Union, List, Coroutine, Callable

import arrow
from aiohttp import WSMessage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ..sdk import RestSdkAbstract, WebsocketSdkAbstract
from ..schemas.logs import LogMsgFmt


class MonitorAbstract(ABC):
    _rest_sdk_class: RestSdkAbstract
    _ws_sdk_class: WebsocketSdkAbstract


    def __init__(self,
                 symbols: List[str],
                 scheduler: AsyncIOScheduler,
                 loop: Union[AbstractEventLoop, None]=None):
        self.logger = logging.getLogger(f'monitor.{self.__class__.__name__}')
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self.symbols = symbols
        self.scheduler = scheduler
        self.rest_sdk = self._rest_sdk_class(self._loop)
        self.ws_sdk = self._ws_sdk_class(self._loop)

    def _run_later(self,
                   coro: Coroutine,
                   args: Union[None, tuple]=None,
                   kwargs: Union[None, dict]=None,
                   sec: int=5):
        """run task in {sec} seconds"""
        self.scheduler.add_job(
            coro,
            args=args,
            kwargs=kwargs,
            trigger='date',
            next_run_time=arrow.utcnow().shift(seconds=sec).naive
        )

    def dispatch_ws_msg(self, msg: WSMessage):
        raise NotImplemented

    def run_ws_in_background(self, handler: Callable=None, sec: int=5):
        if handler is None:
            handler = self.dispatch_ws_msg
        self._run_later(self.ws_sdk.keep_connect,
                        args=(handler,),
                        sec=sec)

    @abstractmethod
    async def schedule(self):
        pass

    def _log_msg(self, msg):
        log_msg = LogMsgFmt.WS_RECV_MSG.value.format(msg=msg)
        self.logger.debug(log_msg)

    def _log_sub_msg(self, msg):
        log_msg = LogMsgFmt.WS_SUB_MSG.value.format(msg=msg)
        self.logger.info(log_msg)


from .okex_future import *
from .okex_spot import *
from .binance import *