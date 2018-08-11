"""
author: thomaszdxsn
"""
import json
import gzip

import pytest

from src.sdk.huobi import HuobiRest, HuobiWebsocket


@pytest.fixture
def sdk(loop):
    yield HuobiRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield HuobiWebsocket(loop)


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker('btcusdt')
    assert msg.error == 0
    assert msg.data['status'] == 'ok'
    assert 'tick' in msg.data
    assert 'ch' in msg.data


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth('btcusdt')
    assert msg.error == 0
    assert len(msg.data['tick']['asks']) == 150
    assert len(msg.data['tick']['bids']) == 150


@pytest.mark.rest
def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline('btcusdt')
    assert msg.error == 0
    assert 'kline' in msg.data['ch']


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades('btcusdt')
    assert msg.error == 0
    assert 'trade' in msg.data['ch']


@pytest.mark.ws
async def test_ws_sub_kline_channel(ws_sdk):
    ws_sdk.register_kline('btcusdt')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        result = gzip.decompress(msg.data)
        result = json.loads(result, encoding='ascii')
        if 'subbed' in result or 'ping' in result:
            continue
        assert 'kline' in result['ch']
        assert 'close' in result['tick']
        assert 'open' in result['tick']
        break


@pytest.mark.ws
async def test_ws_sub_ticker_channel(ws_sdk):
    ws_sdk.register_ticker('btcusdt')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        result = gzip.decompress(msg.data)
        result = json.loads(result, encoding='ascii')
        if 'subbed' in result or 'ping' in result:
            continue
        assert 'detail' in result['ch']
        break


@pytest.mark.ws
async def test_ws_sub_depth_channel(ws_sdk):
    ws_sdk.register_depth('btcusdt')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        result = gzip.decompress(msg.data)
        result = json.loads(result, encoding='ascii')
        if 'subbed' in result or 'ping' in result:
            continue
        assert 'depth' in result['ch']
        break


@pytest.mark.ws
async def test_ws_sub_trades_channel(ws_sdk):
    ws_sdk.register_trades('btcusdt')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        result = gzip.decompress(msg.data)
        result = json.loads(result, encoding='ascii')
        if 'subbed' in result or 'ping' in result:
            continue
        assert 'trade' in result['ch']
        break


