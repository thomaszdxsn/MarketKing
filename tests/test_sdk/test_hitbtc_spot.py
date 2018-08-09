"""
Author: thomaszdxsn
"""
import json

import pytest

from src.sdk.hitbtc_spot import HitBTCSpotRest, HitBTCSpotWebsocket


@pytest.fixture
def sdk(loop):
    yield HitBTCSpotRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield HitBTCSpotWebsocket(loop)


def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker('ethbtc')
    assert msg.error == 0
    assert 'open' in msg.data
    assert 'last' in msg.data
    assert 'bid' in msg.data


def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth('ethbtc')
    assert msg.error == 0
    assert isinstance(msg.data['ask'], list)
    assert isinstance(msg.data['bid'], list)


def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline('ethbtc')
    assert msg.error == 0
    assert isinstance(msg.data, list)


def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades('ethbtc')
    assert msg.error == 0
    assert isinstance(msg.data, list)


@pytest.mark.ws
async def test_ws_sub_ticker_channel(ws_sdk):
    ws_sdk.register_ticker('ethbtc')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'method' in data:
            assert data ['method'] == 'ticker'
            break


@pytest.mark.ws
async def test_ws_sub_depth_channel(ws_sdk):
    ws_sdk.register_depth('ethbtc')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'method' in data:
            assert 'Orderbook' in data['method']
            break
            

@pytest.mark.ws
async def test_ws_sub_trades_channel(ws_sdk):
    ws_sdk.register_trades('ethbtc')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'method' in data:
            assert 'Trades' in data['method']
            break


@pytest.mark.ws
async def test_ws_sub_kline_channel(ws_sdk):
    ws_sdk.register_kline('ethbtc')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if 'method' in data:
            assert 'Candles' in data['method']
            break