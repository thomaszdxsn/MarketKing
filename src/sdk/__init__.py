"""
author: thomaszdxsn
"""
import atexit
import logging
from abc import abstractmethod, ABC
from asyncio import AbstractEventLoop
from typing import Union, Callable


from requests import Session
from aiohttp import ClientSession

from ..schemas import Params
from ..schemas.sdk import ResponseMsg
from ..utils import (NoSSlVerifyTCPConnector, close_session,
                     SessionWrapper, AsyncSessionWrapper)


class RestSdkAbstract(ABC):

    def __init__(self, loop: Union[AbstractEventLoop, None]=None):
        self.logger = logging.getLogger(f"sdk.{self.__class__.__name__}")
        self._session = Session()
        self._session_wrapper = SessionWrapper(self._session)
        self._loop = loop
        if loop:
            self._loop = loop
            self._async_session = ClientSession(
                loop=loop,
                trust_env=True,
                connector=NoSSlVerifyTCPConnector()
            )
            self._async_session_wrapper = AsyncSessionWrapper(
                self._async_session
            )
            atexit.register(close_session, self._async_session)

    def _http_get(self, *args, **kwargs) -> ResponseMsg:
        return self._session_wrapper.get(*args, **kwargs)
    
    async def _async_http_get(self, *args, **kwargs) -> ResponseMsg:
        return await self._async_session_wrapper.get(*args, **kwargs)

    def get_kline(self, *args, **kwargs) -> ResponseMsg:
        params = self._kline_request(*args, **kwargs)
        return self._http_get(*params.args,
                              **params.kwargs)

    async def get_kline_async(self, *args, **kwargs):
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
    ws_url: str

    def __init__(self, loop: AbstractEventLoop):
        self.logger = logging.getLogger(f"sdk.{self.__class__.__name__}")
        self._loop = loop
        self._session = ClientSession(
            loop=loop,
            trust_env=True,
            connector=NoSSlVerifyTCPConnector()
        )
        self.ws_client = None
        self.register_hub = list()

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

    async def setup_ws_client(self):
        if self.ws_url is None:
            raise ValueError('class attribute `ws_url` should not be None')
        if self.ws_client is None:
            self.ws_client = await self._session.ws_connect(
                self.ws_url,
                proxy='http://127.0.0.1:1087'
            )
            atexit.register(close_session, self._session)
        return self.ws_client

    @abstractmethod
    async def subscribe(self, *args, **kwargs):
        pass

    @abstractmethod
    async def unsubscribe(self, *args, **kwargs):
        pass

    async def connect(self, handler: Callable):
        await self.setup_ws_client()
        async for msg in self.ws_client:
            handler(msg)

    async def keep_connect(self):
        pass




