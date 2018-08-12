"""
Author: thomaszdxsn
"""
import pytest

from src.sdk.bibox import BiboxRest

symbol = 'BIX_BTC'


@pytest.fixture
def sdk(loop):
    yield BiboxRest(loop)


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker(symbol)
    assert msg.error == 0
    assert symbol == msg.data['result']['pair']
    assert 'last' in msg.data['result']
    assert 'last_cny' in msg.data['result']


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth(symbol)
    assert msg.error == 0
    assert 'bids' in msg.data['result']
    assert 'asks' in msg.data['result']


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades(symbol)
    assert msg.error == 0
    assert 'side' in msg.data['result'][0]


@pytest.mark.rest
def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline(symbol)
    assert msg.error == 0
    k_item = msg.data['result'][0]
    assert 'open' in k_item
    assert 'close' in k_item



