"""
author: thomaszdxsn
"""
import json

import pytest

from src.sdk.coinbase_pro import *

symbol = 'BTC-USD'


@pytest.fixture
def sdk(loop):
    yield CoinbaseProRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield CoinbaseProWebsocket(loop)


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth(symbol)
    assert msg.error == 0
    assert 'asks' in msg.data
    assert 'bids' in msg.data


@pytest.mark.rest
def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline(symbol)
    assert msg.error == 0
    assert len(msg.data) >= 299


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades(symbol)
    assert msg.error == 0
    assert 'side' in msg.data[0]
    assert 'trade_id' in msg.data[0]


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker(symbol)
    assert msg.error == 0
    assert 'trade_id' in msg.data
    assert 'bid' in msg.data
    assert 'volume' in msg.data


@pytest.mark.skip
@pytest.mark.ws
async def test_ws_sub_ticker_channel(ws_sdk):
    ws_sdk.register_ticker(symbol)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if data['type'] == 'subscription':
            continue
        assert data['type'] == 'ticker'
        break


@pytest.mark.skip
@pytest.mark.ws
async def test_ws_sub_depth_channel(ws_sdk):
    ws_sdk.register_depth(symbol)
    ws_sdk.register_ticker(symbol)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        print(data)
        break
