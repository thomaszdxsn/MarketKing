"""
author: thomaszdxsn
"""
import asyncio
import logging
import pathlib
import os
from datetime import datetime, timedelta

import arrow
from arrow import Arrow
from dynaconf import settings
from tqdm import tqdm

from src.backup.s3 import S3Backup
from src.storage.mongo import MongoStorage
from src.schemas.backup import S3Record
from src.utils import compress_file

logger = logging.getLogger(__name__)
EXPORT_FILES_DIR = pathlib.Path(__file__).parent / 'export_files/'
EXPORT_FILES_DIR.mkdir(exist_ok=True)


class Mongo2S3Command(object):

    def __init__(self, start: datetime, end: datetime):
        assert end - start <= timedelta(days=1), 'interval must be lte one day'
        self.start = start
        self.end = end
        self.start_date = f"{start:%Y-%m-%d}"
        self.out_sep = '+'
        self.mongo_storage = MongoStorage(
            settings.MONGO_URI,
            settings.as_int('MONGO_POOL_SIZE')
        )
        self.backup = S3Backup(
            access_key_id=settings['AWS_ACCESS_KEY_ID'],
            secret_access_key=settings['AWS_SECRET_ACCESS_KEY']
        )
        report_db = settings['MONGO_REPORT_DATABASE']
        s3_coll_name = settings['MONGO_S3_SYNC_COLLECTION']
        self.s3_coll = self.mongo_storage._mongo_client[report_db][s3_coll_name]
        self.s3_bucket = settings['S3_BUCKET']
        self.s3_presign_url_expire = settings['S3_PRESIGN_URL_EXPIRE']

    async def save_record(self, s3_record):
        dct = s3_record.to_dict()
        await self.s3_coll.update_one(
            {
                'collection': dct['collection'],
                'pair': dct['pair'],
                'date': dct['date']
            },
            {"$set": dct},
            upsert=True
        )

    async def record_exists(self, coll: str, pair: str) -> bool:
        return (await self.s3_coll.find_one(
            {
                'collection': coll,
                'pair': pair,
                'date': arrow.get(self.start_date).naive
            }
        )) is not None

    async def to_csv(self, coll: str, query: dict,
                     pair: str, fields: list, out: str) -> S3Record:
        s3_record = S3Record(
            collection=coll,
            pair=pair,
            date=arrow.get(self.start_date).naive,
        )
        out_csv = EXPORT_FILES_DIR / f"{out}.csv"
        out_csv_gzip = EXPORT_FILES_DIR / f"{out}.csv.gz"
        cmd = self.mongo_storage.build_mongoexport_cmd(
            coll_name=coll,
            query=query,
            fields=fields,
            out=str(out_csv.resolve())
        )
        process = await asyncio.create_subprocess_shell(
            cmd,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()
        await process.wait()
        if process.returncode != 0:
            logger.error('error in mongoexport: {}'.format(stderr))
        else:
            compress_file(out_csv, out_csv_gzip)
            s3_record.is_export = True
            s3_record.local_file = str(out_csv_gzip)
            s3_record.size = out_csv_gzip.stat().st_size
        await self.save_record(s3_record)
        return s3_record

    async def to_s3(self, s3_record: S3Record):
        s3_key = self._build_s3_key(s3_record.collection,
                                    s3_record.pair)
        try:
            with open(s3_record.local_file, 'rb') as f:
                is_upload = await self.backup.upload(
                    self.s3_bucket,
                    s3_key,
                    f
                )
        except Exception as exc:
            logger.error('error in s3 uploading')
            is_upload = False
        else:
            os.remove(s3_record.local_file)
            s3_record.s3_key = s3_key
            s3_record.presign_url = (await self.build_presigned_url(s3_key))
        s3_record.is_upload = is_upload
        await self.save_record(s3_record)

    async def build_presigned_url(self, s3_key) -> str:
        return await self.backup.gen_presigned_url(
            self.s3_bucket,
            s3_key,
            self.s3_presign_url_expire
        )

    async def iter_pairs(self, coll: str):
        pairs = await self.mongo_storage.get_collection_pairs(
            coll,
            start=self.start,
            end=self.end
        )
        desc = f'{self.start_date}-{coll}'
        for pair in tqdm(pairs, desc=desc):
            if await self.record_exists(coll, pair):
                # skip when exists
                logger.info(f"{self.start_date}-{coll}-{pair} 已经存在，跳过")
                continue
            fields = await self.mongo_storage.get_collection_fields(coll)
            # remove redundant field
            fields.remove('_id')
            fields.remove('pair')
            out_name = self._build_out_name(coll, pair)
            query = self._build_query(pair)
            s3_record = await self.to_csv(coll, query, pair, fields, out_name)
            if s3_record.is_export is False:
                # error occur in mongoexport
                continue
            await self.to_s3(s3_record)
            logger.info(f"{self.start_date}-{coll}-{pair} 已经上传")

    def _build_query(self, pair: str) -> dict:
        return {
            'pair': pair,
            'created': {
                '$gte': self.start,
                '$lt': self.end
            }
        }

    def _build_out_name(self, coll: str, pair: str) -> str:
        out_fields = [coll, pair, self.start_date]
        return self.out_sep.join(out_fields)

    def _build_s3_key(self, coll: str, pair: str) -> str:
        # 替换separator
        name = self._build_out_name(coll, pair).replace(self.out_sep, '/')
        return f"{name}.csv.gz"

    async def main(self):
        collections = await self.mongo_storage.list_collections()
        for coll in collections:
            if coll.startswith('system'):
                continue
            await self.iter_pairs(coll)


async def main(start: Arrow, end: Arrow):
    for day_start, day_end in arrow.Arrow.span_range('day', start, end):
        cmd = Mongo2S3Command(day_start.naive, day_end.naive)
        await cmd.main()
