"""
author: thomaszdxsn
"""
import pytest

from src.sdk.okex_future import OkexFutureRest, OkexFutureWebsocket


@pytest.fixture
def sdk(loop):
    yield OkexFutureRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield OkexFutureWebsocket(loop)


def test_get_ticker_by_rest(sdk):
    msg = sdk.get_ticker('btc_usd', 'this_week')
    assert msg.error == 0
    assert 'date' in msg.data
    assert 'ticker' in msg.data


async def test_async_get_ticker_by_rest(sdk):
    msg = await sdk.get_ticker_async('btc_usd', 'this_week')
    assert msg.error == 0
    assert 'date' in msg.data
    assert 'ticker' in msg.data


def test_get_depth_by_rest(sdk):
    msg = sdk.get_depth('btc_usd', 'this_week')
    assert msg.error == 0
    assert 'asks' in msg.data
    assert 'bids' in msg.data
    assert len(msg.data['asks']) <= 20
    assert len(msg.data['asks']) <= 20


def test_get_depth_size_arg_by_rest(sdk):
    msg = sdk.get_depth('btc_usd', 'this_week', size=50, merge=False)
    assert msg.error == 0
    assert 'asks' in msg.data
    assert 'bids' in msg.data
    assert 20 < len(msg.data['asks']) <= 50
    assert 20 < len(msg.data['asks']) <= 50

def test_get_trades_by_rest(sdk):
    msg = sdk.get_trades('btc_usd', 'this_week')
    assert msg.error == 0
    assert isinstance(msg.data, list)


def test_get_kline_by_rest(sdk):
    msg = sdk.get_kline('btc_usd', '1min', 'this_week')
    assert msg.error == 0
    assert isinstance(msg.data, list)


@pytest.mark.ws
async def test_get_data_from_websocket(ws_sdk):
    symbol = 'btc'
    contract_type = 'this_week'
    ws_sdk.register_kline(symbol, contract_type)
    ws_sdk.register_depth(symbol, contract_type)
    ws_sdk.register_trades(symbol, contract_type)
    ws_sdk.register_ticker(symbol, contract_type)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        assert 'channel' in msg.data
        break