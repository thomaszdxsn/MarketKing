"""
Author: thomaszdxsn
"""
import json

import pytest

from src.sdk.bitmex import BitmexWebsocket

symbol = 'XBTUSD'


@pytest.fixture
def ws_sdk(loop):
    yield BitmexWebsocket(loop)


@pytest.mark.ws
async def test_ws_sub_trade_bin_channel(ws_sdk):
    ws_sdk.register_trade_bin(symbol, '1m')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'table' not in data:
            continue
        assert data['table'] == 'tradeBin1m'
        break


@pytest.mark.ws
async def test_ws_sub_trades_channel(ws_sdk):
    ws_sdk.register_trades(symbol)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'table' not in data:
            continue
        assert data['table'] == 'trade'
        assert 'side' in data['data'][0]
        break


@pytest.mark.ws
async def test_ws_sub_quote_bin_channel(ws_sdk):
    ws_sdk.register_quote_bin(symbol, '1m')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'table' not in data:
            continue
        assert data['table'] == 'quoteBin1m'
        assert 'bidSize' in data['data'][0]
        break


@pytest.mark.ws
async def test_ws_sub_instrument(ws_sdk):
    ws_sdk.register_instrument(symbol)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'table' not in data:
            continue
        assert data['table'] == 'instrument'
        break


@pytest.mark.ws
async def test_ws_sub_settlement(ws_sdk):
    ws_sdk.register_settlement()
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'table' not in data:
            continue
        assert data['table'] == 'settlement'
        break


@pytest.mark.ws
async def test_ws_sub_depth10(ws_sdk):
    ws_sdk.register_orderbook10(symbol)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'table' not in data:
            continue
        assert data['table'] == 'orderBook10'
        break
