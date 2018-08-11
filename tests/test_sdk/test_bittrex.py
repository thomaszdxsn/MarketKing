"""
Author: thomaszdxsn
"""
import pytest

from src.sdk.bittrex import BittrexRest

symbol = 'BTC-LTC'


@pytest.fixture
def sdk(loop):
    yield BittrexRest(loop)


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker(symbol)
    assert msg.error == 0
    assert 'BaseVolume' in msg.data['result'][0]


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth(symbol)
    assert msg.error == 0
    assert 'buy' in msg.data['result']
    assert 'sell' in msg.data['result']


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades(symbol)
    assert msg.error == 0
    assert 'FillType' in msg.data['result'][0]
