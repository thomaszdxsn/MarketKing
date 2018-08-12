"""
author: thomaszdxsn
"""
import asyncio
from asyncio import AbstractEventLoop
from abc import ABC, abstractmethod
from typing import Union, List, Coroutine, Callable

import arrow
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ..sdk import RestSdkAbstract, WebsocketSdkAbstract


class MonitorAbstract(ABC):
    _rest_sdk_class: RestSdkAbstract
    _ws_sdk_class: WebsocketSdkAbstract


    def __init__(self,
                 symbols: List[str],
                 scheduler: AsyncIOScheduler,
                 loop: Union[AbstractEventLoop, None]=None):
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

    def dispatch_ws_msg(self, msg):
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