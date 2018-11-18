"""
author: thomaszdxsn
"""
import asyncio

from tqdm import tqdm

from src.backup.s3 import s3_backup_factory
from src.backup.oss import oss_backup_factory


s3_bakcup = s3_backup_factory()
oss_backup = oss_backup_factory()


async def iterate_bucket_items(bucket):
    async with s3_bakcup.create_client() as client:
        pagiantor = client.get_paginator('list_objects_v2')
        page_iterator = pagiantor.paginate(Bucket=bucket)

        async for page in page_iterator:
            for item in tqdm(page['Contents']):
                yield item


async def copy_obj(key):
    # 判断oss是否存在key
    if await oss_backup.exists(key):
        print('exists')
        return
    async with s3_bakcup.create_client() as client:
        response = await client.get_object(Bucket='dquant1', Key=key)
        async with response['Body'] as stream:
            body = await stream.read()
            await oss_backup.upload(key, body)
        print(f"{key} downloaded!!!")


async def main():
    keys = []
    async for item in iterate_bucket_items('dquant1'):
        key = item['Key']
        await copy_obj(key)



asyncio.get_event_loop().run_until_complete(main())
