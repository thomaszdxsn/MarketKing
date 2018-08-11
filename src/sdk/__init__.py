"""
author: thomaszdxsn
"""
import atexit
import logging
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
    _async_timeout: ClientTimeout = ClientTimeout(
        total=_request_conn_timeout + _request_read_timeout,
        sock_connect=_request_conn_timeout,
        sock_read=_request_read_timeout
    )
    _http_proxy: Union[str, None] = settings['HTTP_PROXY']
    _headers: Union[dict, None] = None

    def __init__(self, loop: Union[AbstractEventLoop, None]=None):
        self.logger = logging.getLogger(f"sdk.{self.__class__.__name__}")
        self._session = Session()
        self._session_wrapper = SessionWrapper(self._session)
        self._loop = loop
        self._requests_proxies = {
            'http': self._http_proxy,
            'https': self._http_proxy
        }
        if loop:
            self._loop = loop
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

        timeout_tuple = (self._request_read_timeout, self._request_conn_timeout)
        kwargs.setdefault('timeout', timeout_tuple)
        kwargs.setdefault('proxies', self._requests_proxies)
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
        raise NotImplemented

    def get_depth(self, *args, **kwargs) -> ResponseMsg:
        params = self._depth_request(*args, **kwargs)
        return self._http_get(*params.args,
                              **params.kwargs)

    async def get_depth_async(self, *args, **kwargs) -> ResponseMsg:
        params = self._depth_request(*args, **kwargs)
        return await self._async_http_get(*params.args,
                                          **params.kwargs)

    def _depth_request(self, *args, **kwargs) -> Params:
        raise NotImplemented

    def get_ticker(self, *args, **kwargs) -> ResponseMsg:
        params = self._ticker_request(*args, **kwargs)
        return self._http_get(*params.args,
                              **params.kwargs)

    async def get_ticker_async(self, *args, **kwargs) -> ResponseMsg:
        params = self._ticker_request(*args, **kwargs)
        return await self._async_http_get(*params.args,
                                          **params.kwargs)

    def _ticker_request(self, *args, **kwargs) -> Params:
        raise NotImplemented

    def get_trades(self, *args, **kwargs) -> ResponseMsg:
        params = self._trades_request(*args, **kwargs)
        return self._http_get(*params.args,
                              **params.kwargs)

    async def get_trades_async(self, *args, **kwargs) -> ResponseMsg:
        params = self._trades_request(*args, **kwargs)
        return await self._async_http_get(*params.args,
                                          **params.kwargs)

    def _trades_request(self, *args, **kwargs) -> Params:
        raise NotImplemented


class WebsocketSdkAbstract(ABC):
    """
    运行流程:
    register_xxx |> setup_ws_client |> subscribe |> connect
    """
    _request_read_timeout: float = settings.as_float('REQUEST_READ_TIMEOUT')
    _request_conn_timeout: float = settings.as_float('REQUEST_CONN_TIMEOUT')
    _async_timeout: ClientTimeout = ClientTimeout(
        total=_request_conn_timeout + _request_read_timeout,
        sock_connect=_request_conn_timeout,
        sock_read=_request_read_timeout
    )
    _ws_timeout: float = settings.as_float('WS_TIMEOUT')
    _ws_recv_timeout: float = settings.as_float('WS_RECV_TIMEOUT')
    _ws_heartbeat: float = settings.as_float('WS_HEARTBEAT')
    _http_proxy: Union[str, None] = settings['HTTP_PROXY']
    ws_url: str

    def __init__(self, loop: AbstractEventLoop):
        self.logger = logging.getLogger(f"sdk.{self.__class__.__name__}")
        self._loop = loop
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
        raise NotImplemented

    def register_depth(self, *args, **kwargs):
        raise NotImplemented

    def register_trades(self, *args, **kwargs):
        raise NotImplemented

    def register_ticker(self, *args, **kwargs):
        raise NotImplemented

    async def setup_ws_client(self) -> ClientWebSocketResponse:
        if self.ws_url is None:
            raise ValueError('class attribute `ws_url` should not be None')
        if self.ws_client is None:
            self.ws_client = await self._session.ws_connect(
                self.ws_url,
                proxy=self._http_proxy,
                timeout=self._ws_timeout,
                receive_timeout=self._ws_recv_timeout,
                heartbeat=self._ws_heartbeat
            )
            atexit.register(close_session, self.ws_client)
        return self.ws_client

    async def subscribe(self, *args, **kwargs):
        for channel_info in self.register_hub:
            await self.ws_client.send_json(channel_info)

    async def connect(self, handler: Callable):
        await self.setup_ws_client()
        async for msg in self.ws_client:
            handler(msg)





