"""
author: thomaszdxsn
"""
import asyncio
import pytest

from src.schemas.items import ExchangeItem
from src.tunnels.queues import QueueTunnel


@pytest.fixture
def items():
    data = []
    for exchange, data_type in zip(
        ['okex_future', 'okex_spot', 'binance', 'bitfinex'],
        ['depth', 'trades', 'kline', 'ticker']
    ):
        data.append(ExchangeItem(
            exchange=exchange,
            data_type=data_type,
            data={}
        ))
    return data


@pytest.fixture
def tunnel():
    yield QueueTunnel()


def test_put_items_in_tunnel(items, tunnel):
    list(map(tunnel.put, items))
    assert len(tunnel) == 4             # 4 keys


def test_get_item_from_tunnel(items, tunnel):
    list(map(tunnel.put, items))
    result = list(map(tunnel.get, [i.id for i in items]))
    assert result == items


async def test_async_get_item_and_sync_put(tunnel, loop):
    item = ExchangeItem(exchange='1', data_type='1', data={})

    async def put_item():
        for i in range(3):
            tunnel.put(item)
            await asyncio.sleep(0.2)
    t = loop.create_task(put_item())

    for i in range(3):
        value = await tunnel.get_async(item.id)
        assert value == item

    t.cancel()