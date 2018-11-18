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

from src.backup.oss import OssBackup
from src.storage.mongo import MongoStorage
from src.schemas.backup import OssRecord
from src.utils import compress_file

logger = logging.getLogger(__name__)
EXPORT_FILES_DIR = pathlib.Path(__file__).parent / 'export_files/'
EXPORT_FILES_DIR.mkdir(exist_ok=True)


class Mongo2OssCommand(object):
    
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
        self.backup = OssBackup(
            access_key_id=settings['OSS_ACCESS_KEY_ID'],
            access_key_secret=settings['OSS_ACCESS_KEY_SECRET'],
            bucket_name=settings['OSS_BUCKET'],
            endpoint=settings['OSS_ENDPOINT'] 
        )
        report_db = settings['MONGO_REPORT_DATABASE']
        oss_coll_name = settings['MONGO_OSS_SYNC_COLLECTION']
        self.oss_coll = self.mongo_storage._mongo_client[report_db][oss_coll_name] 
        
    async def save_record(self, oss_record: OssRecord):
        dct = oss_record.to_dict()
        await self.oss_coll.update_one(
            {
                'collection': dct['collection'],
                'pair': dct['pair'],
                'date': dct['date']
            },
            {"$set": dct},
            upsert=True
        )
        
    async def record_exists(self, coll: str, pair: str) -> bool:
        return (await self.oss_coll.find_one(
            {
                'collection': coll,
                'pair': pair,
                'date': arrow.get(self.start_date).naive
            }
        )) is not None
    
    async def to_csv(self, coll: str, query: dict,
                     pair: str, fields: list, out: str) -> OssRecord:
        oss_record = OssRecord(
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
            oss_record.is_export = True
            oss_record.local_file = str(out_csv_gzip)
            oss_record.size = out_csv_gzip.stat().st_size
        await self.save_record(oss_record)
        return oss_record

    async def to_oss(self, oss_record: OssRecord):
        oss_key = self._build_oss_key(oss_record.collection,
                                      oss_record.pair)
        try:
            with open(oss_record.local_file, 'rb') as f:
                is_upload = await self.backup.upload(
                    oss_key,
                    f
                )
        except Exception as exc:
            logger.error('error in oss uploading')
            is_upload = False
        else:
            os.remove(oss_record.local_file)
            oss_record.oss_key = oss_key
            oss_record.presign_url = (await self.build_presigned_url(oss_key))
        oss_record.is_upload = is_upload
        await self.save_record(oss_record)

    async def build_presigned_url(self, oss_key) -> str:
        return await self.backup.gen_presigned_url(
            oss_key,
            settings['OSS_PRESIGN_URL_EXPIRE']
        )

    def _build_out_name(self, coll: str, pair: str) -> str:
        out_fields = [coll, pair, self.start_date]
        return self.out_sep.join(out_fields)

    def _build_oss_key(self, coll: str, pair: str) -> str:
        # 替换separator
        name = self._build_out_name(coll, pair).replace(self.out_sep, '/')
        return f"{name}.csv.gz"

    def _build_query(self, pair: str) -> dict:
        return {
            'pair': pair,
            'created': {
                '$gte': self.start,
                '$lt': self.end
            }
        }

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
            oss_record = await self.to_csv(coll, query, pair, fields, out_name)
            if oss_record.is_export is False:
                # error occur in mongoexport
                continue
            await self.to_oss(oss_record)
            logger.info(f"{self.start_date}-{coll}-{pair} 已经上传")

    async def main(self):
        collections = await self.mongo_storage.list_collections()
        for coll in collections:
            if coll.startswith('system'):
                continue
            await self.iter_pairs(coll)


async def main(start: Arrow, end: Arrow):
    for day_start, day_end in arrow.Arrow.span_range('day', start, end):
        cmd = Mongo2OssCommand(day_start.naive, day_end.naive)
        await cmd.main()