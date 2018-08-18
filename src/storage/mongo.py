"""
author: thomaszdxsn
"""
from dynaconf import settings
from pymongo import InsertOne, UpdateOne, ReplaceOne, WriteConcern
from pymongo.errors import BulkWriteError
from motor.motor_asyncio import AsyncIOMotorClient

from . import StorageAbstract
from ..schemas.logs import LogMsgFmt
from ..tunnels import TunnelAbstract


class MongoStorage(StorageAbstract):
    batch_op_size: int = int(settings.get('MONGO_BATCH_OP_SIZE', 30))

    def __init__(self):
        super(MongoStorage, self).__init__()
        self._mongo_client = AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=settings.as_int('MONGO_POOL_SIZE')
        )

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

    async def bulk_op(self, database: str, collection: str,
                      items: list, ordered: bool=False):
        coll = self._mongo_client[database].get_collection(
            collection, write_concern=WriteConcern(w=0, wtimeout=2)     # not ack
        )
        requests = []
        for item in items:
            data_item = item.data
            data_item_dict = data_item.to_dict()
            unique_fields = data_item.get_unique_indexes()
            if not unique_fields:
                requests.append(InsertOne(data_item_dict))
            else:
                upsert_op = ReplaceOne(
                    {
                        f: data_item_dict[f]
                        for f in unique_fields
                    },
                    data_item_dict,
                    upsert=True
                )
                requests.append(upsert_op)
        result = await coll.bulk_write(requests, ordered=ordered)
        if result.acknowledged:
            msg = LogMsgFmt.MONGO_OPS.value.format(
                f"{database}|{collection}|{result.bulk_api_result}"
            )
            if result.bulk_api_result['writeErrors']:
                self.logger.warning(msg)
            else:
                self.logger.debug(msg)

    async def worker(self,
                     tunnel: TunnelAbstract,
                     id_: str):
        database = settings['MONGO_DATABASE']
        exchange, data_type  = id_.split('|')
        collection = f'{exchange}0{data_type}'      # 以0作为交易所和数据类型之间的分隔符
        while True:
            try:
                items = await self.fetch_n_items(tunnel,
                                                 id_,
                                                 self.batch_op_size)
                await self.bulk_op(database, collection, items)
            except BulkWriteError as bwe:
                msg = str(bwe.details)
                self.logger.error(msg)
            except Exception as exc:
                msg = LogMsgFmt.EXCEPTION.value.format(exc=exc)
                self.logger.error(msg)
