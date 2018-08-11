"""
Author: thomaszdxsn
"""
from urllib.parse import urljoin

from . import WebsocketSdkAbstract
from ..schemas import Params

__all__ = (
    'BitmexWebsocket',
)


class BitmexWebsocket(WebsocketSdkAbstract):
    """
    doc: https://www.bitmex.com/app/wsAPI 
    """
    ws_url = 'wss://www.bitmex.com/realtime'

    async def subscribe(self, *args, **kwargs):
        sub_msg = {
            'op': 'subscribe',
            'args': self.register_hub
        }
        await self.ws_client.send_json(sub_msg)

    def register_trade_bin(self, symbol: str, type_: str='1m'):
        """
        doc: {type_} trade bins
        """
        type_range = ('1m', '5m', '1h', '1d')
        assert type_ in type_range, f'type_ must be one of {type_range}'
        channel_info = f'tradeBin{type_}:{symbol}'
        self.register_channel(channel_info)

    def register_trades(self, symbol: str):
        """
        doc: Live trades
        """
        channel_info = f'trade:{symbol}'
        self.register_channel(channel_info)

    def register_quote_bin(self, symbol: str, type_: str='1m'):
        """
        doc: {type_} quote bins 
        """        
        channel_info = f'quoteBin{type_}:{symbol}'
        self.register_channel(channel_info) 

    def register_kline(self, symbol):
        channel_info = f'insurance'
        self.register_channel(channel_info)