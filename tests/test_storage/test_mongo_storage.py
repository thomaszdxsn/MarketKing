"""
author: thomaszdxsn
"""
import arrow
import pytest
from dynaconf import settings

from src.storage.mongo import MongoStorage


@pytest.fixture
def mongo_storage(loop):
    return MongoStorage(
        settings.MONGO_URI,
        settings.as_int('MONGO_POOL_SIZE')
    )


async def test_list_collections(mongo_storage):
    collections = await mongo_storage.list_collections()
    for collection_name in collections:
        if collection_name.startswith('system'):
            continue
        assert '0' in collection_name


async def test_get_collections_fields(mongo_storage):
    coll_name = (await mongo_storage.list_collections())[0]
    fields = await mongo_storage.get_collection_fields(coll_name)
    assert '_id' in fields
    assert 'pair' in fields


async def test_get_pairs(mongo_storage):
    coll_name = (await mongo_storage.list_collections())[0]
    utcnow = arrow.utcnow()
    start, end = utcnow.shift(years=-1).naive, utcnow.naive
    pairs = await mongo_storage.get_collection_pairs(coll_name,
                                                     start,
                                                     end)
    assert any(['btc' in pair.lower() for pair in pairs])


async def test_build_mongo_export_cmd(mongo_storage):
    query = {'pair': 'btcusdt'}
    fields = ['created', 'pair']
    cmd = mongo_storage.build_mongoexport_cmd(
        coll_name='bitflyer0depth',
        query=query,
        fields=fields,
        out='out.csv'
    )
    assert '\n' not in cmd
