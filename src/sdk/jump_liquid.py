"""
author: thomaszdxsn
"""
from . import WebsocketSdkAbstract


class JumpLiquidWebsocket(WebsocketSdkAbstract):
    ws_url = 'wss://www.liquidcryptotrading.com/traderWorkstationWS'