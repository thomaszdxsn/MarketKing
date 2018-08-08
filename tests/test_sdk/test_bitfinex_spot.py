"""
author: thomaszdxsn
"""
import json

import pytest

from src.sdk.bitfinex_spot import BitfinexRest, BitfinexWebsocket


@pytest.fixture
def sdk(loop):
    yield BitfinexRest(loop)


@pytest.fixture
def ws_sdk(loop):
    yield BitfinexWebsocket(loop)


def test_get_ticker_from_rest(sdk):
    msg = sdk.get_ticker('btcusd')
    assert msg.error == 0
    assert type(msg.data) == list


def test_get_kline_from_rest(sdk):
    msg = sdk.get_kline('btcusd')
    assert msg.error == 0
    assert type(msg.data) == list


def test_get_trades_from_rest(sdk):
    msg = sdk.get_trades('btcusd')
    assert msg.error == 0
    assert type(msg.data) == list


def test_get_depth_from_rest(sdk):
    msg = sdk.get_depth('btcusd')
    assert msg.error == 0
    assert type(msg.data) == list


async def test_ws_sub_ticker_channel(ws_sdk):
    ws_sdk.register_ticker('btcusd')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if isinstance(data, dict):
            continue
        if isinstance(data, list):
            assert isinstance(data[0], int)
            break


async def test_ws_sub_depth_channel(ws_sdk):
    ws_sdk.register_depth('btcusd')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if isinstance(data, dict):
            continue
        if isinstance(data, list):
            assert isinstance(data[0], int)
            break


async def test_ws_sub_trades_channel(ws_sdk):
    ws_sdk.register_trades('btcusd')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if isinstance(data, dict):
            continue
        if isinstance(data, list):
            assert isinstance(data[0], int)
            break


async def test_ws_sub_kline_channel(ws_sdk):
    ws_sdk.register_kline('btcusd')
    await ws_sdk.setup_ws_client()
    await ws_sdk.subscribe()
    async for msg in ws_sdk.ws_client:
        data = json.loads(msg.data)
        if isinstance(data, dict):
            continue
        if isinstance(data, list):
            assert isinstance(data[0], int)
            break
