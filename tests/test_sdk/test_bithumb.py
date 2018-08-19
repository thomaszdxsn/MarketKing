"""
Author: thomaszdxsn
"""
import pytest

from src.sdk.bithumb import BithumbRest

symbol = 'BTC'


@pytest.fixture
def sdk(loop):
    yield BithumbRest(loop)


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker(symbol)
    assert msg.error == 0
    assert 'opening_price' in msg.data['data']
    assert 'closing_price' in msg.data['data']


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth(symbol)
    assert msg.error == 0
    assert 'bids' in msg.data['data']
    assert 'asks' in msg.data['data']


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades(symbol)
    assert msg.error == 0
    assert 'transaction_date' in msg.data['data'][0]