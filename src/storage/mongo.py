"""
author: thomaszdxsn
"""
from datetime import datetime
from typing import List

from dynaconf import settings
from pymongo import InsertOne, UpdateOne, ReplaceOne, WriteConcern
from pymongo.errors import BulkWriteError
from motor.motor_asyncio import AsyncIOMotorClient

from . import StorageAbstract
from ..schemas.logs import LogMsgFmt
from ..tunnels import TunnelAbstract

__all__ = (
    'MongoStorage',
)


class MongoStorage(StorageAbstract):
    batch_op_size: int = int(settings.get('MONGO_BATCH_OP_SIZE', 30))

    def __init__(self, uri, pool_size):
        super(MongoStorage, self).__init__()
        self._mongo_client = AsyncIOMotorClient(
            uri,
            maxPoolSize=pool_size
        )
        self._data_db = self._mongo_client[settings['MONGO_DATABASE']]
        self._separator = '0'

    async def fetch_n_items(self,
                            tunnel: TunnelAbstract,
                            id_: str,
                            n: int) -> list:
        items = []
        while True:
            item = await tunnel.get_async(id_)
            items.append(item)
            if len(items) >= n:
                return items

    async def bulk_op(self, collection: str,
                      items: list, ordered: bool=False):
        coll = self._data_db.get_collection(
            collection, write_concern=WriteConcern(w=0, wtimeout=2)     # not ack
        )
        requests = []
        for item in items:
            data_item = item.data
            data_item_dict = data_item.to_dict()
            unique_fields = data_item.get_unique_indexes()
            if not unique_fields or not collection.endswith('kline'):   # don't upsert trades
                requests.append(InsertOne(data_item_dict))
            else:                                                       # upsert is too expensive, only do it for kline
                upsert_op = ReplaceOne(
                    {
                        f: data_item_dict[f]
                        for f in unique_fields
                    },
                    data_item_dict,
                    upsert=True
                )
                requests.append(upsert_op)
        ordered = ordered if not collection.endswith('kline') else True
        result = await coll.bulk_write(requests, ordered=ordered)
        if result.acknowledged:
            msg = LogMsgFmt.MONGO_OPS.value.format(
                f"{collection}|{result.bulk_api_result}"
            )
            if result.bulk_api_result['writeErrors']:
                self.logger.warning(msg)
            else:
                self.logger.debug(msg)

    async def worker(self,
                     tunnel: TunnelAbstract,
                     id_: str):
        exchange, data_type  = id_.split('|')
        collection = f'{exchange}{self._separator}{data_type}'      # 以0作为交易所和数据类型之间的分隔符
        while True:
            try:
                items = await self.fetch_n_items(tunnel,
                                                 id_,
                                                 self.batch_op_size)
                await self.bulk_op(collection, items)
            except BulkWriteError as bwe:
                msg = str(bwe.details)
                self.logger.error(msg)
            except Exception as exc:
                msg = LogMsgFmt.EXCEPTION.value.format(exc=exc)
                self.logger.error(msg)

    async def list_collections(self) -> List[str]:
        return await self._data_db.list_collection_names()

    async def get_collection_fields(self, coll_name: str) -> List[str]:
        doc = await self._data_db[coll_name].find_one()
        return list(doc.keys())

    async def get_collection_pairs(self,
                                   coll_name: str,
                                   start: datetime,
                                   end: datetime) -> List[str]:
        coll = self._data_db[coll_name]
        filter_ = {
            'created': {
                '$gte': start,
                '$lt': end
            }
        }
        return await coll.distinct('pair', filter_)


def mongoexport_cmd():
    pass