"""
author: thomaszdxsn
"""
import json

import pytest

from src.sdk.fcoin import FcoinRest, FcoinWebsocket


@pytest.fixture
def sdk(loop):
    yield FcoinRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield FcoinWebsocket(loop)


@pytest.mark.rest
def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline('ftbtc')
    assert msg.error == 0
    assert msg.data['status'] == 0
    assert len(msg.data['data']) == 20


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades('ftbtc')
    assert msg.error == 0
    assert msg.data['status'] == 0


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth('ftbtc')
    assert msg.error == 0
    assert msg.data['status'] == 0
    assert 'bids' in msg.data['data']
    assert 'asks' in msg.data['data']


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker('ftbtc')
    assert msg.error == 0
    assert msg.data['status'] == 0


@pytest.mark.ws
async def test_ws_sub_ticker_channel(ws_sdk):
    ws_sdk.register_ticker('ftusdt')
    ws_sdk.register_ticker('ftbtc')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()

    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        assert 'type' in data
        if 'ticker' not  in data:
            continue
        else:
            break


@pytest.mark.ws
async def test_ws_sub_depth_channel(ws_sdk):
    ws_sdk.register_depth('ftusdt')
    ws_sdk.register_depth('ftbtc')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()

    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        assert 'type' in data
        if 'asks' not in data:
            continue
        else:
            break


@pytest.mark.ws
async def test_ws_sub_kline_channel(ws_sdk):
    ws_sdk.register_kline('ftusdt')
    ws_sdk.register_kline('ftbtc')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()

    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        assert 'type' in data
        if 'open' not in data:
            continue
        else:
            break


@pytest.mark.ws
async def test_ws_sub_trades_channel(ws_sdk):
    ws_sdk.register_trades('ftusdt')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()

    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        assert 'type' in data
        if 'trade' not in data['type']:
            continue
        else:
            break