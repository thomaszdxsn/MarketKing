"""
author: thomaszdxsn
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Union, Any

import aiohttp
import requests
from requests import Session
from aiohttp import ClientSession, ClientWebSocketResponse

from .schemas.sdk import ResponseMsg, HttpErrorEnum


def close_session(session: ClientSession):
    """handler for atexit"""
    asyncio.run(session.close())


class NoSSlVerifyTCPConnector(aiohttp.TCPConnector):

    def __init__(self, *args, verify_ssl=False, **kwargs):
        super(NoSSlVerifyTCPConnector, self).__init__(*args,
                                                      verify_ssl=verify_ssl,
                                                      **kwargs)


class SessionWrapperAbstract(ABC):

    def __init__(self, session: Union[Session, ClientSession]):
        self.session = session
        self.logger = logging.getLogger(f"sdk.{self.__class__.__name__}")

    @abstractmethod
    def get(self, *args, **kwargs) -> ResponseMsg:
        pass

    @abstractmethod
    def post(self, *args, **kwargs) -> ResponseMsg:
        pass

    @abstractmethod
    def request(self, http_method: str, *args,
                resp_method: str='json', **kwargs) -> ResponseMsg:
        pass


class AsyncSessionWrapper(SessionWrapperAbstract):

    async def get(self, *args, **kwargs) -> ResponseMsg:
        return await self.request('get', *args, **kwargs)

    async def post(self, *args, **kwargs) -> ResponseMsg:
        return await self.request('post', *args, **kwargs)

    async def request(self, http_method: str, *args,
                      resp_method: str='json', **kwargs) -> ResponseMsg:
        method = getattr(self.session, http_method)
        try:
            async with method(*args, **kwargs) as resp:
                resp_handler = getattr(resp, resp_method)
                result = await (resp_handler() if callable(
                                resp_handler) else resp_handler)
                return ResponseMsg(
                    data=result
                )
        except aiohttp.client_exceptions.ClientError as exc:
            msg = f'client error in request: {exc}, {args}, {kwargs}'
            self.logger.error(msg, exc_info=True)
            return ResponseMsg(
                error=HttpErrorEnum.ClientError.value,
                data=''
            )
        except Exception as exc:
            msg = f"other error in request: {exc} {args}, {kwargs}"
            self.logger.error(msg, exc_info=True)
            return ResponseMsg(
                error=HttpErrorEnum.OtherError.value,
                data=''
            )


class SessionWrapper(SessionWrapperAbstract):

    def get(self, *args, **kwargs) -> ResponseMsg:
        return self.request('get', *args, **kwargs)

    def post(self, *args, **kwargs) -> ResponseMsg:
        return self.request('post', *args, **kwargs)

    def request(self, http_method: str, *args,
                resp_method: str='json', **kwargs) -> ResponseMsg:
        try:
            method = getattr(self.session, http_method)
            resp = method(*args, **kwargs)
            resp_handler = getattr(resp, resp_method)
            result = resp_handler() if callable(resp_handler) else resp_handler
            return ResponseMsg(
                data=result
            )
        except requests.RequestException as exc:
            msg = f'client error in request: {exc} {args}, {kwargs}'
            self.logger.error(msg, exc_info=True)
            return ResponseMsg(
                error=HttpErrorEnum.ClientError.value,
                data=''
            )
        except Exception as exc:
            msg = f"other error in request: {exc} {args}, {kwargs}"
            self.logger.error(msg, exc_info=True)
            return ResponseMsg(
                error=HttpErrorEnum.OtherError.value,
                data=''
            )