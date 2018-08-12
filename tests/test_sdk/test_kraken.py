"""
author: thomaszdxsn
"""
import pytest

from src.sdk.kraken import *

pair = 'XBTEUR'


@pytest.fixture
def sdk(loop):
    yield KrakenRest(loop)


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker(pair)
    assert msg.error == 0
    assert 'XXBTZEUR' in msg.data['result']


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth(pair)
    assert msg.error == 0
    assert 'asks' in msg.data['result']['XXBTZEUR']
    assert 'bids' in msg.data['result']['XXBTZEUR']


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades(pair)
    assert msg.error == 0
    assert 'XXBTZEUR' in msg.data['result']
    assert msg.data['result']['XXBTZEUR'][0][-3] in ('b', 's')


@pytest.mark.rest
def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline(pair)
    assert msg.error == 0
    assert 'XXBTZEUR' in msg.data['result']