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
from ..schemas import DataClassAbstract
from ..schemas.logs import LogMsgFmt
from ..schemas.items import Item, ExchangeItem
from ..tunnels import TunnelAbstract


class MonitorAbstract(ABC):
    exchange: str
    _rest_sdk_class: Union[RestSdkAbstract, None]=None
    _ws_sdk_class: Union[WebsocketSdkAbstract, None]=None

    def __init__(self,
                 symbols: List[str],
                 scheduler: AsyncIOScheduler,
                 tunnel: TunnelAbstract,
                 loop: Union[AbstractEventLoop, None]=None):
        self.logger = logging.getLogger(f'monitor.{self.__class__.__name__}')
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self.symbols = symbols
        self._depth_interval = 1
        self.scheduler = scheduler
        self.tunnel = tunnel
        self.rest_sdk = self._rest_sdk_class(self._loop) \
                            if self._rest_sdk_class else None
        self.ws_sdk = self._ws_sdk_class(self._loop)    \
                            if self._ws_sdk_class else None

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

    def build_item(self,
                   data_type:str,
                   data: DataClassAbstract) -> ExchangeItem:
        return ExchangeItem(
            exchange=self.exchange,
            data_type=data_type,
            data=data
        )

    def tunnel_put(self, item: ExchangeItem):
        self.tunnel.put(item)

    async def tunnel_put_async(self, item: ExchangeItem):
        await self.tunnel.put(item)

    def transport(self, data_type: str, data: DataClassAbstract):
        item = self.build_item(data_type, data)
        self.tunnel_put(item)


from .okex_spot import *
from .okex_future import *
from .bitflyer import *
from .binance import *
from .bitfinex import *
from .huobi import *
from .bitmex import *
from .hitbtc import *
from .poloniex import *

MONITOR_MAP = {
    'okex_future': OkexFutureMonitor,
    'okex_spot': OkexSpotMonitor,
    'huobi': HuobiMonitor,
    'bitfinex': BitfinexMonitor,
    'binance': BinanceMonitor,
    'bitflyer': BitflyerMonitor,
    'bitmex': BitmexMonitor,
    'hitbtc': HitBTCMonitor,
    'poloniex': PoloniexMonitor
}