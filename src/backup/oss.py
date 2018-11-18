"""
author: thomaszdxsn
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from asyncio import AbstractEventLoop
from typing import Optional

import oss2
from dynaconf import settings

from . import BackupAbstract
from ..schemas.logs import LogMsgFmt


class OssBackup(BackupAbstract):

    def __init__(self, access_key_id: str, access_key_secret: str,
                 endpoint: str, bucket_name: str, loop: Optional[AbstractEventLoop]=None):
        super(OssBackup, self).__init__()
        self._thread_executor = ThreadPoolExecutor()
        self._auth = oss2.Auth(access_key_id, access_key_secret)
        self._bucket = oss2.Bucket(self._auth, endpoint, bucket_name)
        self._loop = loop if loop else asyncio.get_event_loop()

    def _upload(self, key: str, body, bucket_name: Optional[str]=None, endpoint: Optional[str]=None) -> bool:
        # sync way
        bucket = oss2.Bucket(self._auth, endpoint, bucket_name) if bucket_name else self._bucket
        try:
            result = bucket.put_object(key, body)
            return True if result.status == 200 else False
        except Exception as exc:
            msg = LogMsgFmt.EXCEPTION.value.format(exc=exc)
            self.logger.error(msg, exc_info=True)
            return False

    async def upload(self, key: str, body,
                     bucket_name: Optional[str]=None, endpoint: Optional[str]=None) -> bool:
        return await self._loop.run_in_executor(self._thread_executor, self._upload, key, body, bucket_name, endpoint)

    def _gen_presigned_url(self, key: str, expire_delta: int) -> str:
        return self._bucket.sign_url('GET', key, expire_delta)

    async def gen_presigned_url(self, key: str, expire_delta: int) -> str:
        return await self._loop.run_in_executor(self._thread_executor, self._gen_presigned_url, key, expire_delta)

    async def exists(self, key: str) -> bool:
        return await self._loop.run_in_executor(self._thread_executor, self._bucket.object_exists, key)


def oss_backup_factory():
    return OssBackup(
        access_key_id=settings['OSS_ACCESS_KEY_ID'],
        access_key_secret=settings['OSS_ACCESS_KEY_SECRET'],
        endpoint=settings['OSS_ENDPOINT'],
        bucket_name=settings['OSS_BUCKET']
    )
