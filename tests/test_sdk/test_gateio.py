"""
Author: thomaszdxsn
"""
import json

import pytest

from src.sdk.gateio import GateIORest, GateIOWebsocket


@pytest.fixture
def sdk(loop):
    yield GateIORest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield GateIOWebsocket(loop)


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth('btc_usdt')
    assert msg.error == 0
    assert 'asks' in msg.data
    assert 'bids' in msg.data


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades('btc_usdt')
    assert msg.error == 0
    assert isinstance(msg.data['data'], list)


@pytest.mark.rest
def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline('btc_usdt')
    assert msg.error == 0
    assert len(msg.data['data']) >= 60


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker('btc_usdt')
    assert msg.error == 0
    assert 'high24hr' in msg.data


@pytest.mark.ws
async def test_ws_sub_ticker_channel(ws_sdk):
    symbol, id_ = 'btc_usdt', 1
    ws_sdk.register_ticker(symbol, id_)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if data['id'] == id_:
            assert 'period' in data['result']
            assert 'quoteVolume' in data['result']
            break


@pytest.mark.ws
async def test_ws_sub_depth_channel(ws_sdk):
    symbol, id_ = 'eos_btc', 1
    ws_sdk.register_depth(symbol, id_)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if data['id'] == id_:
            assert 'asks' in data['result']
            assert 'bids' in data['result']
            break


@pytest.mark.ws
async def test_ws_sub_trades_channel(ws_sdk):
    symbol, id_ = 'eth_usdt', 1
    ws_sdk.register_trades(symbol, id_)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if data['id'] == id_:
            assert 'id' in data['result'][0]
            assert 'type' in data['result'][0]
            break


@pytest.mark.ws
async def test_ws_sub_kline_channel(ws_sdk):
    symbol, id_ = 'eth_usdt', 1
    ws_sdk.register_kline(symbol, id_)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if data['id'] == id_:
            assert len(data['result']) >= 1000
            break