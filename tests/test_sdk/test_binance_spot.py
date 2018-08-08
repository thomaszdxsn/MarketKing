"""
author: thomaszdxsn
"""
import pytest

from src.sdk.binance_spot import BinanceSpotRest


@pytest.fixture
def sdk(loop):
    yield BinanceSpotRest(loop)


def test_get_kline_from_rest(sdk):
    res = sdk.get_kline('BTCUSDT')
    assert res.error == 0
    assert len(res.data) == 500


def test_get_trades_from_rest(sdk):
    res = sdk.get_trades('BTCUSDT')
    assert res.error == 0
    assert len(res.data) == 500


def test_get_ticker_from_rest(sdk):
    res = sdk.get_ticker('BTCUSDT')
    assert res.error == 0
    assert res.data['symbol'] == 'BTCUSDT'


def test_get_depth_from_resk(sdk):
    res = sdk.get_depth('BTCUSDT')
    assert res.error == 0
    assert len(res.data['asks']) == 100
    assert len(res.data['bids']) == 100
