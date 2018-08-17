"""
author: thomaszdxsn
"""
from dynaconf import settings
from pymongo import InsertOne, UpdateOne, ReplaceOne
from motor.motor_asyncio import AsyncIOMotorClient

from . import StorageAbstract
from ..schemas.logs import LogMsgFmt
from ..tunnels import TunnelAbstract


class MongoStorage(StorageAbstract):

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
        coll = self._mongo_client[database][collection]
        requests = []
        for item in items:
            requests.append(InsertOne(item.data.to_dict()))
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
                     id_: str,
                     items_num=10):
        database = settings['MONGO_DATABASE']
        exchange, data_type  = id_.split('|')
        collection = f'{exchange}0{data_type}'
        while True:
            try:
                items = await self.fetch_n_items(tunnel, id_, items_num)
                await self.bulk_op(database, collection, items)
            except Exception as exc:
                print(database, collection, exc)
