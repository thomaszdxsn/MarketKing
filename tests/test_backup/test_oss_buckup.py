"""
author: thomaszdxsn
"""
import pytest
from dynaconf import settings

from src.backup.oss import OssBackup


@pytest.fixture
def oss_backup(loop):
    return OssBackup(
        access_key_id=settings['OSS_ACCESS_KEY_ID'],
        access_key_secret=settings['OSS_ACCESS_KEY_SECRET'],
        endpoint=settings['OSS_ENDPOINT'],
        bucket_name=settings['OSS_BUCKET']
    )


async def test_upload_object_to_oss(oss_backup):
    key = 'tests/dummy.bin'
    body = b'\x01' * 1024
    assert await oss_backup.upload(key, body) == True


async def test_gen_sign_url(oss_backup):
    key = 'tests/dummy.bin'
    presign_url = await oss_backup.gen_presigned_url(key, 60)
    assert presign_url
