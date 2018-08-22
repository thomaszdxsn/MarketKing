"""
author: thomaszdxsn
"""
import functools

import aiobotocore

from . import BackupAbstract
from ..schemas.logs import LogMsgFmt


class S3Backup(BackupAbstract):

    def __init__(self, access_key_id: str, secret_access_key: str):
        super(S3Backup, self).__init__()
        self.session = aiobotocore.get_session()
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self.create_client = functools.partial(
            self.session.create_client,
            's3',
            aws_secret_access_key=self._secret_access_key,
            aws_access_key_id=self._access_key_id
        )

    async def upload(self, bucket: str, key: str, body: bytes) -> bool:
        async with self.create_client() as client:
            try:
                await client.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=body
                )

                waiter = client.get_waiter('object_exists')
                await waiter.wait(Bucket=bucket, Key=key)
            except Exception as exc:
                msg = LogMsgFmt.EXCEPTION.value.format(exc=exc)
                self.logger.error(msg, exc_info=True)
                return False
            return True



