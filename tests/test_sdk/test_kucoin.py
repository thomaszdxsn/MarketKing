"""
Author: thomaszdxsn
"""
import pytest

from src.sdk.kucoin import KucoinRest

symbol = 'ETH-BTC'


@pytest.fixture
def sdk(loop):
    yield KucoinRest(loop)


@pytest.mark.rest
def test_get_kline_from_sdk(sdk):
    msg = sdk.get_kline(symbol)
    assert msg.error == 0
    assert msg.data['success'] == True
    assert isinstance(msg.data['data'], list)


@pytest.mark.rest
def test_get_depth_from_sdk(sdk):
    msg = sdk.get_depth(symbol)
    assert msg.error == 0
    assert msg.data['success'] == True
    assert 'SELL' in msg.data['data']
    assert 'BUY' in msg.data['data']


@pytest.mark.rest
def test_get_ticker_from_sdk(sdk):
    msg = sdk.get_ticker(symbol)
    assert msg.error == 0
    assert 'lastDealPrice' in msg.data['data']
    assert 'datetime' in msg.data['data']


@pytest.mark.rest
def test_get_trades_from_sdk(sdk):
    msg = sdk.get_trades(symbol)
    assert msg.error == 0
    buy_or_sell = msg.data['data'][0][1]
    assert buy_or_sell in ('BUY', "SELL")


