"""
Author: thomaszdxsn
"""
import asyncio

from . import WebsocketSdkAbstract
from ..utils import chunk

__all__ = (
    'BitmexWebsocket',
)


class BitmexWebsocket(WebsocketSdkAbstract):
    """
    doc: https://www.bitmex.com/app/wsAPI 
    """
    ws_url = 'wss://www.bitmex.com/realtime'

    async def subscribe(self, *args, **kwargs):
        if not self.ws_client:
            await self.setup_ws_client()
        # 参数不能过长
        for args in chunk(self.register_hub, 10):
            sub_msg = {
                'op': 'subscribe',
                'args': args
            }
            await self.ws_client.send_json(sub_msg)
            await asyncio.sleep(1)

    def register_trade_bin(self, symbol: str, type_: str='1m'):
        """
        desc: {type_} trade bins
        """
        type_range = ('1m', '5m', '1h', '1d')
        assert type_ in type_range, f'type_ must be one of {type_range}'
        channel_info = f'tradeBin{type_}:{symbol.upper()}'
        self.register_channel(channel_info)

    def register_trades(self, symbol: str):
        """
        desc: Live trades
        """
        channel_info = f'trade:{symbol.upper()}'
        self.register_channel(channel_info)

    def register_quote_bin(self, symbol: str, type_: str='1m'):
        """
        desc: {type_} quote bins 
        """        
        type_range = ('1m', '5m', '1h', '1d')
        assert type_ in type_range, f'type_ must be one of {type_range}'
        channel_info = f'quoteBin{type_}:{symbol.upper()}'
        self.register_channel(channel_info) 

    def register_instrument(self, symbol: str):
        """
        desc: instrument updates including turnover and bid/ask
        """
        channel_info = f'instrument:{symbol.upper()}'
        self.register_channel(channel_info)

    def register_settlement(self):
        """
        desc: Settlements
        """
        channel_info = 'settlement'
        self.register_channel(channel_info)

    def register_orderbook10(self, symbol: str):
        channel_info = f'orderBook10:{symbol.upper()}'
        self.register_channel(channel_info)
    