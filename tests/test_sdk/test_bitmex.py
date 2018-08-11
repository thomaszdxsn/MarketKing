"""
Author: thomaszdxsn
"""
import pytest

from src.sdk.bitmex import BitmexWebsocket

symbol = 'XBTUSD'


@pytest.fixture
def ws_sdk(loop):
    yield BitmexWebsocket(loop)


# @pytest.mark.ws
# async def test_ws_sub_kline_channel(ws_sdk):
#     ws_sdk.register_kline(symbol)
#     await ws_sdk.setup_ws_client()
#     await ws_sdk.subscribe()
#     async for msg in ws_sdk.ws_client:
#         print(msg)