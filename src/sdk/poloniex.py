"""
Author: thomaszdxsn
"""
from urllib.parse import urljoin
from typing import Union

from . import WebsocketSdkAbstract, RestSdkAbstract
from ..schemas import Params

__all__ = (
    'PoloniexRest',
    'PoloniexWebsocket'
)


class PoloniexRest(RestSdkAbstract):
    """
    doc: https://poloniex.com/support/api/
    """
    base_url = 'https://poloniex.com/'
    public_url = urljoin(base_url, '/public')

    def _ticker_request(self) -> Params:
        """Returns the ticker for all markets"""
        request_data = {
            'params': {
                'command': 'returnTicker'
            }
        }
        return Params(
            args=(self.public_url,),
            kwargs=request_data
        )

    def _depth_request(self, 
                       currency_pair: str,
                       depth: int=20) -> Params:
        request_data = {
            'params': {
                'command': 'returnOrderBook',
                'currencyPair': currency_pair.upper(),
                'depth': depth
            }
        }
        return Params(
            args=(self.public_url,),
            kwargs=request_data
        )

    def _trades_request(self,
                        currency_pair: str,
                        start: int,
                        end: int) -> Params:
        request_data = {
            'params': {
                'command': 'returnTradeHistory',
                'currencyPair': currency_pair.upper(),
                'start': start,
                'end': end
            }
        }
        return Params(
            args=(self.public_url,),
            kwargs=request_data
        )

    def _kline_request(self,
                       currency_pair: str,
                       start: int,
                       end: int,
                       period: int=300) -> Params:
        request_data = {
            'params': {
                'command': 'returnChartData',
                'currencyPair': currency_pair.upper(),
                'start': start,
                'end': end,
                'period': period
            }
        }
        return Params(
            args=(self.public_url,),
            kwargs=request_data
        )


class PoloniexWebsocket(WebsocketSdkAbstract):
    ws_url = 'wss://api2.poloniex.com'

    def register_ticker(self):
        """Subscribe to ticker updates for all currency pairs."""
        channel_info = {
            'command': 'subscribe',
            'channel': 1002
        }
        self.register_channel(channel_info)

    def register_depth(self, currency_pair: Union[str, int]):
        channel_info = {
            'command': 'subscribe',
            'channel': currency_pair.upper() \
                    if isinstance(currency_pair, str) else currency_pair 
        }
        self.register_channel(channel_info)


SYMBOLS_MAP = {
    7: "BTC_BCN",
    12: "BTC_BTCD",
    13: "BTC_BTM",
    14: "BTC_BTS",
    15: "BTC_BURST",
    20: "BTC_CLAM",
    24: "BTC_DASH",
    25: "BTC_DGB",
    27: "BTC_DOGE",
    28: "BTC_EMC2",
    38: "BTC_GAME",
    40: "BTC_GRC",
    43: "BTC_HUC",
    50: "BTC_LTC",
    51: "BTC_MAID",
    58: "BTC_OMNI",
    61: "BTC_NAV",
    63: "BTC_NEOS",
    64: "BTC_NMC",
    69: "BTC_NXT",
    74: "BTC_POT",
    75: "BTC_PPC",
    89: "BTC_STR",
    92: "BTC_SYS",
    97: "BTC_VIA",
    99: "BTC_VRC",
    100: "BTC_VTC",
    104: "BTC_XBC",
    108: "BTC_XCP",
    112: "BTC_XEM",
    114: "BTC_XMR",
    116: "BTC_XPM",
    117: "BTC_XRP",
    121: "USDT_BTC",
    122: "USDT_DASH",
    123: "USDT_LTC",
    124: "USDT_NXT",
    125: "USDT_STR",
    126: "USDT_XMR",
    127: "USDT_XRP",
    129: "XMR_BCN",
    131: "XMR_BTCD",
    132: "XMR_DASH",
    137: "XMR_LTC",
    138: "XMR_MAID",
    140: "XMR_NXT",
    148: "BTC_ETH",
    149: "USDT_ETH",
    150: "BTC_SC",
    153: "BTC_EXP",
    155: "BTC_FCT",
    160: "BTC_AMP",
    162: "BTC_DCR",
    163: "BTC_LSK",
    166: "ETH_LSK",
    167: "BTC_LBC",
    168: "BTC_STEEM",
    169: "ETH_STEEM",
    170: "BTC_SBD",
    171: "BTC_ETC",
    172: "ETH_ETC",
    173: "USDT_ETC",
    174: "BTC_REP",
    175: "USDT_REP",
    176: "ETH_REP",
    177: "BTC_ARDR",
    178: "BTC_ZEC",
    179: "ETH_ZEC",
    180: "USDT_ZEC",
    181: "XMR_ZEC",
    182: "BTC_STRAT",
    184: "BTC_PASC",
    185: "BTC_GNT",
    186: "ETH_GNT",
    187: "BTC_GNO",
    188: "ETH_GNO",
    189: "BTC_BCH",
    190: "ETH_BCH",
    191: "USDT_BCH",
    192: "BTC_ZRX",
    193: "ETH_ZRX",
    194: "BTC_CVC",
    195: "ETH_CVC",
    196: "BTC_OMG",
    197: "ETH_OMG",
    198: "BTC_GAS",
    199: "ETH_GAS",
    200: "BTC_STORJ",
    201: "BTC_EOS",
    202: "ETH_EOS",
    203: "USDT_EOS",
    1002: 'ALL_TICKERS'
}