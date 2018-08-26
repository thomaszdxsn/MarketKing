"""
author: thomaszdxsn
"""
import asyncio
import itertools
import logging
import os
import json
import gzip
import shutil
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Union, Iterable
from functools import partial

import aiohttp
import requests
from requests import Session
from aiohttp import ClientSession

from .schemas.sdk import ResponseMsg, HttpErrorEnum
from .schemas.logs import LogMsgFmt


def compress_file(input_file: Union[str, Path],
                  output_file: Union[str, Path],
                  remove_orig: bool=True) -> None:
    with open(input_file, 'rb') as f1, gzip.open(output_file, 'wb') as f2:
        shutil.copyfileobj(f1, f2)
    if remove_orig:
        os.remove(input_file)


def chunk(it: Iterable, size: int) -> Iterable:
    it = iter(it)
    return iter(lambda: tuple(itertools.islice(it, size)), ())


def close_session(session: ClientSession):
    """handler for atexit"""
    asyncio.run(session.close())


class DatetimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()


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
                if resp_method == 'json':
                    resp_handler = partial(resp_handler, content_type=None)
                result = await (resp_handler() if callable(
                                resp_handler) else resp_handler)

                # log
                url = args[0]
                msg = LogMsgFmt.HTTP_RESPONSE.value.format(
                    method=http_method.upper(),
                    url=url,
                    response=result,
                )
                self.logger.debug(msg)
                return ResponseMsg(
                    data=result
                )
        except aiohttp.client_exceptions.ClientError as exc:
            error_no = HttpErrorEnum.ClientError.value
            exc_msg = LogMsgFmt.EXCEPTION.value.format(exc=exc)
            msg = f'SDKClientError|{error_no}|{exc_msg}|{args}|{kwargs}'
            self.logger.error(msg, exc_info=True)
            return ResponseMsg(
                error=error_no,
                data=''
            )
        except Exception as exc:
            error_no = HttpErrorEnum.OtherError.value
            exc_msg = LogMsgFmt.EXCEPTION.value.format(exc=exc)
            msg = f'SDKClientError|{error_no}|{exc_msg}|{args}|{kwargs}'
            self.logger.error(msg, exc_info=True)
            return ResponseMsg(
                error=error_no,
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

            url = args[0]
            msg = LogMsgFmt.HTTP_RESPONSE.value.format(
                method=http_method.upper(),
                url=url,
                response=result,
            )
            self.logger.debug(msg)
            return ResponseMsg(
                data=result
            )
        except requests.RequestException as exc:
            error_no = HttpErrorEnum.ClientError.value
            exc_msg = LogMsgFmt.EXCEPTION.value.format(exc=exc)
            msg = f'SDKClientError|{error_no}|{exc_msg}|{args}|{kwargs}'
            self.logger.error(msg, exc_info=True)
            return ResponseMsg(
                error=error_no,
                data=''
            )
        except Exception as exc:
            error_no = HttpErrorEnum.OtherError.value
            exc_msg = LogMsgFmt.EXCEPTION.value.format(exc=exc)
            msg = f'SDKClientError|{error_no}|{exc_msg}|{args}|{kwargs}'
            self.logger.error(msg, exc_info=True)
            return ResponseMsg(
                error=error_no,
                data=''
            )


