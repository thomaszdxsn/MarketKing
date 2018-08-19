"""
author: thomaszdxsn
"""
import asyncio
import atexit
import logging
import os
from abc import ABC
from asyncio import AbstractEventLoop
from typing import Union, Callable

from aiohttp import ClientSession, ClientTimeout, ClientWebSocketResponse
from dynaconf import settings
from requests import Session

from ..schemas import Params
from ..schemas.sdk import ResponseMsg
from ..schemas.logs import LogMsgFmt
from ..utils import (NoSSlVerifyTCPConnector, close_session,
                     SessionWrapper, AsyncSessionWrapper)


class RestSdkAbstract(ABC):
    _request_read_timeout: float = settings.as_float('REQUEST_READ_TIMEOUT')
    _request_conn_timeout: float = settings.as_float('REQUEST_CONN_TIMEOUT')
    _headers: Union[dict, None] = None

    def __init__(self, loop: Union[AbstractEventLoop, None]=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self.logger = logging.getLogger(f"sdk.{self.__class__.__name__}")
        self._session = Session()
        self._session_wrapper = SessionWrapper(self._session)
        self._loop = loop
        self._timeout_tuple = (self._request_read_timeout,
                               self._request_conn_timeout)
        # aiohttp related
        self._async_timeout: ClientTimeout = ClientTimeout(
            total=self._request_conn_timeout + self._request_read_timeout,
            sock_connect=self._request_conn_timeout,
            sock_read=self._request_read_timeout
        )
        self._async_session = ClientSession(
            loop=loop,
            trust_env=True,
            connector=NoSSlVerifyTCPConnector(),
            timeout=self._async_timeout
        )
        self._async_session_wrapper = AsyncSessionWrapper(
            self._async_session
        )
        atexit.register(close_session, self._async_session)

    def _http_get(self, *args, **kwargs) -> ResponseMsg:
        # logging
        url = args[0]
        log_msg = LogMsgFmt.HTTP_ACTION.value.format(method='GET', url=url)
        self.logger.info(log_msg)

        kwargs.setdefault('timeout', self._timeout_tuple)
        if self._headers:
            kwargs.setdefault('headers', self._headers)
        return self._session_wrapper.get(*args, **kwargs)
    
    async def _async_http_get(self, *args, **kwargs) -> ResponseMsg:
        url = args[0]
        log_msg = LogMsgFmt.HTTP_ACTION.value.format(method='GET', url=url)
        self.logger.info(log_msg)

        if self._headers:
            kwargs.setdefault('headers', self._headers)
        return await self._async_session_wrapper.get(*args, **kwargs)

    def get_kline(self, *args, **kwargs) -> ResponseMsg:
        params = self._kline_request(*args, **kwargs)
        return self._http_get(*params.args,
                              **params.kwargs)

    async def get_kline_async(self, *args, **kwargs) -> ResponseMsg:
        params = self._kline_request(*args, **kwargs)
        return await self._async_http_get(*params.args,
                                          **params.kwargs)

    def _kline_request(self, *args, **kwargs) -> Params:
        raise NotImplementedError()

    def get_depth(self, *args, **kwargs) -> ResponseMsg:
        params = self._depth_request(*args, **kwargs)
        return self._http_get(*params.args,
                              **params.kwargs)

    async def get_depth_async(self, *args, **kwargs) -> ResponseMsg:
        params = self._depth_request(*args, **kwargs)
        return await self._async_http_get(*params.args,
                                          **params.kwargs)

    def _depth_request(self, *args, **kwargs) -> Params:
        raise NotImplementedError()

    def get_ticker(self, *args, **kwargs) -> ResponseMsg:
        params = self._ticker_request(*args, **kwargs)
        return self._http_get(*params.args,
                              **params.kwargs)

    async def get_ticker_async(self, *args, **kwargs) -> ResponseMsg:
        params = self._ticker_request(*args, **kwargs)
        return await self._async_http_get(*params.args,
                                          **params.kwargs)

    def _ticker_request(self, *args, **kwargs) -> Params:
        raise NotImplementedError()

    def get_trades(self, *args, **kwargs) -> ResponseMsg:
        params = self._trades_request(*args, **kwargs)
        return self._http_get(*params.args,
                              **params.kwargs)

    async def get_trades_async(self, *args, **kwargs) -> ResponseMsg:
        params = self._trades_request(*args, **kwargs)
        return await self._async_http_get(*params.args,
                                          **params.kwargs)

    def _trades_request(self, *args, **kwargs) -> Params:
        raise NotImplementedError()


class WebsocketSdkAbstract(ABC):
    """
    运行流程:
    register_xxx |> setup_ws_client |> subscribe |> connect
    """
    _request_read_timeout: float = settings.as_float('REQUEST_READ_TIMEOUT')
    _request_conn_timeout: float = settings.as_float('REQUEST_CONN_TIMEOUT')
    _ws_timeout: float = settings.as_float('WS_TIMEOUT')
    _ws_recv_timeout: float = settings.as_float('WS_RECV_TIMEOUT')
    _ws_heartbeat: float = settings.as_float('WS_HEARTBEAT')
    _ws_reconnect_interval: float = settings.as_float('WS_RECONNECT_INTERVAL')
    _ws_retry: bool = settings['WS_RETRY_ON_CONNECT_LOST']
    ws_url: str

    def __init__(self, loop: Union[AbstractEventLoop, None]=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self.logger = logging.getLogger(f"sdk.{self.__class__.__name__}")
        self._loop = loop
        self._async_timeout: ClientTimeout = ClientTimeout(
            total=self._request_conn_timeout + self._request_read_timeout,
            sock_connect=self._request_conn_timeout,
            # TODO: read timeout会有一些问题，一些接口会无缘无故抛出TimeoutError
            # sock_read=self._request_read_timeout
        )
        self._session = ClientSession(
            loop=loop,
            trust_env=True,
            connector=NoSSlVerifyTCPConnector(),
            timeout=self._async_timeout
        )
        self.ws_client = None
        self.register_hub = list()
        atexit.register(close_session, self._session)

    def register_channel(self, channel_info):
        self.register_hub.append(channel_info)

    def register_kline(self, *args, **kwargs):
        raise NotImplementedError()

    def register_depth(self, *args, **kwargs):
        raise NotImplementedError()

    def register_trades(self, *args, **kwargs):
        raise NotImplementedError()

    def register_ticker(self, *args, **kwargs):
        raise NotImplementedError()

    async def setup_ws_client(self) -> ClientWebSocketResponse:
        if self.ws_url is None:
            raise ValueError('class attribute `ws_url` should not be None')
        if self.ws_client is None:
            self.ws_client = await self._session.ws_connect(
                self.ws_url,
                proxy=os.environ.get('http_proxy', None),
                timeout=self._ws_timeout,
                receive_timeout=self._ws_recv_timeout,
                heartbeat=self._ws_heartbeat
            )
            atexit.register(close_session, self.ws_client)
        return self.ws_client

    async def subscribe(self, *args, **kwargs):
        while True:
            try:
                if not self.ws_client:
                    await self.setup_ws_client()
                for channel_info in self.register_hub:
                    await self.ws_client.send_json(channel_info)
            except Exception as exc:
                msg = LogMsgFmt.EXCEPTION.value.format(exc=exc)
                self.logger.error(msg, exc_info=True)
                if self._ws_retry:
                    await asyncio.sleep(self._ws_reconnect_interval)
                    self.logger.warning('websocket reconnect...')
                else:
                    raise
            else:
                break

    async def connect(self, handler: Callable):
        async for msg in self.ws_client:
            await handler(msg)

    async def keep_connect(self, handler: Callable):
        while True:
            try:
                await self.connect(handler)
            except Exception as exc:
                msg = LogMsgFmt.EXCEPTION.value.format(exc=exc)
                self.logger.error(msg, exc_info=True)
            finally:
                # reconnect
                # 有时候ws链接会正常关闭，必须重连否则收不到新的消息
                await asyncio.sleep(self._ws_reconnect_interval)
                self.logger.warning('websocket reconnect...')
                await self.ws_client.close()
                self.ws_client = None
                await self.subscribe()




from .bibox import *
from .binance import *
from .bitfinex import *
from .bitflyer import *
from .bithumb import *
from .bitmex import *
from .bitstamp import *
from .bittrex import *
from .bitZ import *
from .coinbase_pro import *
from .cointiger import *
from .digifinex import *
from .fcoin import *
from .gateio import *
from .hitbtc import *
from .huobi import *
from .kraken import *
from .kucoin import *
from .lbank import *
from .okex_future import *
from .okex_spot import *
from .poloniex import *
from .upbit import *
from .zb import *


