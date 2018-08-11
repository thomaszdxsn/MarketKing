"""
Author: thomaszdxsn
"""
import pytest

from src.sdk.bitZ import BitZRest

symbol = 'eth_btc'


@pytest.fixture
def sdk(loop):
    yield BitZRest(loop)


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker(symbol)
    assert msg.error == 0
    assert msg.data['data']['symbol'] == symbol
    assert 'priceChange24h' in msg.data['data']


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth(symbol)
    assert msg.error == 0
    assert 'asks' in msg.data['data']
    assert 'bids' in msg.data['data']


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades(symbol)
    assert msg.error == 0
    assert isinstance(msg.data['data'], list)
    assert 'id' in msg.data['data'][0]


@pytest.mark.rest
def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline(symbol)
    assert msg.error == 0
    assert 'bars' in msg.data['data']