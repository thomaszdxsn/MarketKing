"""
author: thomaszdxsn
"""
import pytest

from src.sdk.bitstamp import BitstampRest

symbol = 'btcusd'


@pytest.fixture
def sdk(loop):
    yield BitstampRest(loop)


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker(symbol)
    assert msg.error == 0
    assert isinstance(msg.data, dict)
    assert 'last' in msg.data
    assert 'open' in msg.data


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades(symbol)
    assert msg.error == 0
    assert isinstance(msg.data, list)
    assert 'tid' in msg.data[0]


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth(symbol)
    assert msg.error == 0
    assert 'bids' in msg.data
    assert 'asks' in msg.data
