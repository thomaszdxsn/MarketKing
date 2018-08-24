"""
author: thomaszdxsn
"""
import json

import arrow
from aiohttp import WSMessage

from . import MonitorAbstract
from ..sdk.bitflyer import BitflyerRest, BitflyerWebsocket
from ..schemas.regexes import BITFLYER_WS_CHANS
from ..schemas.markets import BitFlyerTicker, BitflyerTrades, BitflyerDepth

__all__ = ('BitflyerMonitor',)


class BitflyerMonitor(MonitorAbstract):
    exchange = 'bitflyer'
    _ws_sdk_class = BitflyerWebsocket
    _rest_sdk_class = BitflyerRest

    async def schedule(self):
        for symbol in self.symbols:
            self.ws_sdk.register_depth(symbol)
            self.ws_sdk.register_trades(symbol)
            self.ws_sdk.register_ticker(symbol)
        await self.ws_sdk.subscribe()
        self.run_ws_in_background(handler=self.dispatch_ws_msg)

    async def dispatch_ws_msg(self, msg: WSMessage):
        data = json.loads(msg.data)
        if "method" not in data:
            return
        channel = data["params"]["channel"]
        match_dict = BITFLYER_WS_CHANS.match(channel).groupdict()
        data_type = match_dict["data_type"]
        pair = match_dict["product_code"]
        if data_type == "ticker":
            await self._handle_ticker(data, pair)
        elif data_type == "executions":
            await self._handle_trades(data, pair)
        else:
            await self._handle_depth(data, pair)

    async def _handle_ticker(self, data: dict, pair: str):
        data_dict = data["params"]["message"]
        timestamp = data_dict.pop("timestamp")
        data_dict["server_created"] = arrow.get(timestamp).naive
        data_dict["pair"] = pair
        del data_dict['product_code']
        ticker = BitFlyerTicker(**data_dict)
        self.transport('ticker', ticker)

    async def _handle_trades(self, data: dict, pair: str):
        trades = [
            BitflyerTrades(
                pair=pair,
                tid=str(item["id"]),
                side=item["side"],
                price=item["price"],
                size=item["size"],
                trade_time=arrow.get(item["exec_date"]).naive,
                buy_child_order_acceptance_id=item[
                    "buy_child_order_acceptance_id"
                ],
                sell_child_order_acceptance_id=item[
                    "sell_child_order_acceptance_id"
                ],
            )
            for item in data["params"]["message"]
        ]
        list(map(lambda x: self.transport('trades', x),
                 trades))

    async def _handle_depth(self, data: dict, pair: str, size:int=20):
        # don't need sorted asks or bids
        asks = data['params']['message']['asks'][:size]
        bids = list(reversed(data['params']['message']['bids']))[:size]
        if not asks and not bids:
            return
        depth = BitflyerDepth(
            pair=pair,
            asks=asks,
            bids=bids,
            mid_price=data['params']['message']['mid_price']
        )
        self.transport('depth', depth)
