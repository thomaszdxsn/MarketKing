"""
author: thomaszdxsn
"""
import pytest
from dynaconf import settings

from src.backup.s3 import S3Backup


@pytest.fixture
def s3_backup(loop):
    return S3Backup(
        access_key_id=settings['AWS_ACCESS_KEY_ID'],
        secret_access_key=settings['AWS_SECRET_ACCESS_KEY']
    )


async def test_upload_object_to_s3(s3_backup):
    bucket = 'dquant2'
    key = 'tests/dummy.bin'
    body = b'\x01' * 1024
    assert await s3_backup.upload(bucket, key, body) == True


