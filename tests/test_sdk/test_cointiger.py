"""
Author: thomaszdxsn
"""
import json
import gzip

import pytest

from src.sdk.cointiger import CointigerRest, CointigerWebsocket

symbol = 'btcusdt'


@pytest.fixture
def sdk(loop):
    yield CointigerRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield CointigerWebsocket(loop)


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker(symbol)
    assert msg.error == 0
    assert 'trade_ticker_data' in msg.data['data']
    

@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth(symbol)
    assert msg.error == 0
    assert 'depth_data' in msg.data['data']


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades(symbol, size=100)
    assert msg.error == 0
    assert 'trade_data' in msg.data['data']
    assert msg.data['data']['size'] == 100


@pytest.mark.rest
def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline(symbol)
    assert msg.error == 0
    assert 'kline_data' in msg.data['data']


@pytest.mark.ws
async def test_ws_sub_ticker_channel(ws_sdk):
    ws_sdk.register_ticker(symbol)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        result = gzip.decompress(msg.data)
        result = json.loads(result, encoding='ascii')
        assert 'ticker' in result['channel']
        assert symbol in result['channel']
        break


@pytest.mark.ws
async def test_ws_sub_depth_channel(ws_sdk):
    ws_sdk.register_depth(symbol)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        result = gzip.decompress(msg.data)
        result = json.loads(result, encoding='ascii')
        assert 'depth' in result['channel']
        assert symbol in result['channel']
        break


@pytest.mark.ws
async def test_ws_sub_trades_channel(ws_sdk):
    ws_sdk.register_trades(symbol)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        result = gzip.decompress(msg.data)
        result = json.loads(result, encoding='ascii')
        assert 'trade' in result['channel']
        assert symbol in result['channel']
        break


@pytest.mark.ws
async def test_ws_sub_trades_channel(ws_sdk):
    ws_sdk.register_kline(symbol)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        result = gzip.decompress(msg.data)
        result = json.loads(result, encoding='ascii')
        assert 'kline' in result['channel']
        assert symbol in result['channel']
        break