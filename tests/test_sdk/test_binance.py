"""
author: thomaszdxsn
"""
import pytest

from src.sdk.binance import BinanceRest, BinanceWebsocket


@pytest.fixture
def sdk(loop):
    yield BinanceRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield BinanceWebsocket(loop)


@pytest.mark.rest
def test_get_kline_from_rest(sdk):
    res = sdk.get_kline('BTCUSDT')
    assert res.error == 0
    assert len(res.data) == 500


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    res = sdk.get_trades('BTCUSDT')
    assert res.error == 0
    assert len(res.data) == 500


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    res = sdk.get_ticker('BTCUSDT')
    assert res.error == 0
    assert res.data['symbol'] == 'BTCUSDT'


@pytest.mark.rest
def test_get_depth_from_resk(sdk):
    res = sdk.get_depth('BTCUSDT')
    assert res.error == 0
    assert len(res.data['asks']) == 100
    assert len(res.data['bids']) == 100


@pytest.mark.ws
async def test_get_data_from_websocket(ws_sdk):
    symbol = 'btcusdt'
    ws_sdk.register_kline(symbol)
    ws_sdk.register_depth(symbol)
    ws_sdk.register_trades(symbol)
    ws_sdk.register_ticker(symbol)
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        assert 'stream' in msg.data
        break