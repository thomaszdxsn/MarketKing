"""
author: thomaszdxsn
"""
from motor.motor_asyncio import AsyncIOMotorClient
from dynaconf import settings
from tqdm import tqdm


unique_map = {
    'binance0kline': ('pair', 'start_time'),
    'binance0depth': '',
    'binance0ticker': '',
    'binance0trades': ('tid',),
    'bitfinex0depth': '',
    'bitfinex0kline': ('pair', 'start_time'),
    'bitfinex0ticker': '',
    'bitfinex0trades': ('tid',),
    'bitflyer0depth': '',
    'bitflyer0ticker': '',
    'bitflyer0trades': ('tid',),
    'bitmex0depth': '',
    'bitmex0trade_bin': ('pair', 'start_time'),
    'bitmex0trades': ('tid',),
    'bitmex0quote_bin': ('pair', 'start_time'),
    'bitmex0settlement': ('pair', 'start_time'),
    'huobi0depth': '',
    'huobi0kline': ('pair', 'start_time'),
    'huobi0ticker': '',
    'huobi0trades': ('tid',),
    'okex_future0depth': '',
    'okex_future0kline': ('pair', 'start_time', 'contract_type'),
    'okex_future0ticker': '',
    'okex_future0trades': ('tid',),
    'okex_spot0depth': '',
    'okex_spot0ticker': '',
    'okex_spot0kline': ('pair', 'start_time'),
    'okex_spot0trades': ('tid',),
    'hitbtc0ticker': '',
    'hitbtc0trades': ('tid',),
    'hitbtc0kline': ('pair', 'start_time'),
    'hitbtc0depth': '',
    'poloniex0depth': '',
    'poloniex0ticker': '',
    'poloniex0trades': ('tid',),
    'fcoin0depth': '',
    'fcoin0ticker': '',
    'fcoin0trades': ('tid',),
    'fcoin0kline': ('pair', 'start_time'),
    'cointiger0depth': '',
    'cointiger0ticker': '',
    'cointiger0trades': ('tid',),
    'cointiger0kline': ('pair', 'start_time'),
    'bithumb0ticker': '',
    'bithumb0depth': '',
    'bithumb0trades': ('tid',),
    'zb0ticker': '',
    'zb0depth': '',
    'zb0trades': ('tid',),
    'zb0kline': ('pair', 'start_time'),
}

db = AsyncIOMotorClient(settings['MONGO_URI'])[settings['MONGO_DATABASE']]
ttl_secs = 60 * 60 * 24 * 7

async def create_unique_indexes():
    for coll, unique_fields in tqdm(unique_map.items(),
                                    desc='build unique indexes'):
        if unique_fields:
            collection = db[coll]
            await collection.create_index(
                [
                    (field, 1)
                    for field in unique_fields
                ],
                unique=True, background=True
            )


async def create_ttl_indexes():
    for coll in tqdm(unique_map.keys(),
                     desc='build ttl indexes'):
        collection = db[coll]
        await collection.create_index('created',
                                      background=True,
                                      expireAfterSeconds=ttl_secs)


async def create_filter_indexes():
    for coll in tqdm(unique_map.keys(),
                     desc='build filter indexes'):
        collection = db[coll]
        await collection.create_index([('created', 1), ('pair', 1)],
                                      background=True)


async def main():
    await create_unique_indexes()
    await create_ttl_indexes()
    await create_filter_indexes()


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

