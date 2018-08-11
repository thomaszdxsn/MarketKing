"""
Author: thomaszdxsn
"""
import json

import arrow
import pytest

from src.sdk.poloniex import PoloniexRest, PoloniexWebsocket


@pytest.fixture
def sdk(loop):
    yield PoloniexRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield PoloniexWebsocket(loop)


@pytest.mark.rest
def test_get_kline_from_sdk(sdk):
    utcnow = arrow.utcnow()
    start = utcnow.shift(hours=-1).timestamp
    end = utcnow.timestamp
    msg = sdk.get_kline('USDT_BTC', start=start, end=end)
    assert msg.error == 0
    assert isinstance(msg.data, list)


@pytest.mark.rest
def test_get_ticker_from_sdk(sdk):
    msg = sdk.get_ticker()
    assert msg.error == 0
    assert isinstance(msg.data, dict)


@pytest.mark.rest
def test_get_depth_from_sdk(sdk):
    msg = sdk.get_depth('usdt_btc')
    assert msg.error == 0
    assert 'asks' in msg.data
    assert 'bids' in msg.data


@pytest.mark.rest
def test_get_trades_from_sdk(sdk):
    utcnow = arrow.utcnow()
    start = utcnow.shift(hours=-1).timestamp
    end = utcnow.timestamp
    msg = sdk.get_trades('usdt_btc', start=start, end=end)
    assert msg.error == 0
    assert isinstance(msg.data, list)


@pytest.mark.ws
async def test_ws_sub_ticker_channels(ws_sdk):
    ws_sdk.register_ticker()
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data, encoding='ascii')
        assert data[0] == 1002
        break


@pytest.mark.ws
async def test_ws_sub_depth_channel(ws_sdk):
    ws_sdk.register_depth('121')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data, encoding='ascii')
        assert data[0] == 121
        break