"""
Author: thomaszdxsn
"""
import json

import pytest

from src.sdk.zb import ZBRest, ZBWebsocket


@pytest.fixture
def sdk(loop):
    yield ZBRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield ZBWebsocket(loop)


@pytest.mark.rest
def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline('zbusdt')
    assert msg.error == 0
    assert msg.data['symbol'] == 'zb'
    assert len(msg.data['data']) == 1000


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth('zbusdt')
    assert msg.error == 0
    assert 'asks' in msg.data
    assert 'bids' in msg.data


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker('zbusdt')
    assert msg.error == 0
    assert 'ticker' in msg.data


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades('zbusdt')
    assert msg.error == 0
    assert isinstance(msg.data, list)


@pytest.mark.ws
async def test_ws_sub_ticker_channel(ws_sdk):
    ws_sdk.register_ticker('zbusdt')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        assert 'ticker' in data['channel']
        break


@pytest.mark.ws
async def test_ws_sub_trades_channel(ws_sdk):
    ws_sdk.register_trades('zbusdt')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        assert 'trades' in data['channel']
        break


@pytest.mark.ws
async def test_ws_sub_depth_channel(ws_sdk):
    ws_sdk.register_depth('zbusdt')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        assert 'depth' in data['channel']
        break