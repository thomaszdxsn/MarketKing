"""
Author: thomaszdxsn
"""
import json
import pytest

from src.sdk.okex_spot import OkexSpotRest, OkexSpotWebsocket


@pytest.fixture
def sdk(loop):
    yield OkexSpotRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield OkexSpotWebsocket(loop)


def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker('ltc_usdt')
    assert msg.error == 0
    assert 'date' in msg.data
    assert 'ticker' in msg.data


def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth('btc_usdt', size=200)
    assert msg.error == 0
    assert 'asks' in msg.data
    assert 'bids' in msg.data
    assert len(msg.data['asks']) == 200


def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades('btc_usdt')
    assert msg.error == 0


def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline('btc_usdt', type_='1min')
    assert msg.error == 0


@pytest.mark.ws
async def test_get_data_from_websocket(ws_sdk):
    symbol = 'btc_usdt'
    ws_sdk.register_depth(symbol, 20)
    ws_sdk.register_depth(symbol, 10)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        assert 'channel' in msg.data
        break