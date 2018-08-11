"""
Author: thomaszdxsn
"""
import asyncio
import json

import pytest

from src.sdk.lbank import LBankRest, LBankWebsocket

symbol = 'eth_btc'


@pytest.fixture
def sdk(loop):
    yield LBankRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield LBankWebsocket(loop)


@pytest.mark.rest
def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker(symbol)
    assert msg.error == 0
    assert msg.data['symbol'] == symbol
    assert 'ticker' in msg.data


@pytest.mark.rest
def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth(symbol)
    assert msg.error == 0
    assert 'asks' in msg.data
    assert 'bids' in msg.data


@pytest.mark.rest
def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline(symbol)
    assert msg.error == 0
    assert isinstance(msg.data, list)


@pytest.mark.rest
def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades(symbol)
    assert msg.error == 0
    assert isinstance(msg.data, list)


# 2018.08.11 尝试国内通过代理进行ws连接的时候会失败
# 失败原因是 ws handshake error, status code 是 400 而不是 101
# TODO: 在境外服务器试一下
# @pytest.mark.skip
# @pytest.mark.ws
# async def test_ws_sub_ticker_channel(ws_sdk):
#     ws_sdk.register_ticker(symbol)
#     await ws_sdk.setup_ws_client()
#     await ws_sdk.subscribe()
#     async for msg in ws_sdk.ws_client:
#         print(msg)