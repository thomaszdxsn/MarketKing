"""
Author: thomaszdxsn
"""
import json

import pytest

from src.sdk.bitflyer import BitflyerRest, BitflyerWebsocket


@pytest.fixture
def sdk(loop):
    yield BitflyerRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield BitflyerWebsocket(loop)


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker('BTC_USD')
    assert msg.error == 0
    assert 'best_ask' in msg.data


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth('BTC_USD')
    assert msg.error == 0
    assert 'asks' in msg.data
    assert 'bids' in msg.data


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades('BTC_USD')
    assert msg.error == 0
    assert isinstance(msg.data, list)


@pytest.mark.ws
async def test_ws_sub_depth_channel(ws_sdk):
    ws_sdk.register_depth('BTC_USD')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'method' in data:
            assert 'lightning_board_snapshot' in data['params']['channel']
            break


@pytest.mark.ws
async def test_ws_sub_ticker_channel(ws_sdk):
    ws_sdk.register_ticker('BTC_USD')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'method' in data:
            assert 'lightning_ticker' in data['params']['channel']
            break


@pytest.mark.ws
async def test_ws_sub_trades_channel(ws_sdk):
    ws_sdk.register_trades('BTC_JPY')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'method' in data:
            assert 'lightning_executions' in data['params']['channel']
            break