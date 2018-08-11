"""
author: thomaszdxsn
"""
import pytest

from src.sdk.upbit import UpbitRest

symbol = 'KRW-BTC'


@pytest.fixture
def sdk(loop):
    yield UpbitRest(loop)


def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker(symbol)
    assert msg.error == 0
    assert msg.data[0]['market'] == symbol
    assert 'acc_trade_price_24h' in msg.data[0]


def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline(symbol)
    assert msg.error == 0
    assert msg.data[0]['market'] == symbol


def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades(symbol)
    assert msg.error == 0
    assert msg.data[0]['market'] == symbol


def test_get_depth_from_rest(sdk):
    markets = ['KRW-ADA', symbol]
    msg = sdk.get_depth(markets)
    assert msg.error == 0
    assert [i['market'] for i in msg.data] == markets

