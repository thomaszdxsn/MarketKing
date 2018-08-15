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


class BitflyerMonitor(MonitorAbstract):
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
        product_code = match_dict["product_code"]
        if data_type == "ticker":
            await self._handle_ticker(data, product_code)
        elif data_type == "executions":
            await self._handle_trades(data, product_code)
        else:
            await self._handle_depth(data, product_code)

    async def _handle_ticker(self, data: dict, product_code: str):
        data_dict = data["params"]["message"]
        timestamp = data_dict.pop("timestamp")
        data_dict["server_created"] = arrow.get(timestamp).naive
        data_dict["product_code"] = product_code
        ticker = BitFlyerTicker(**data_dict)

    async def _handle_trades(self, data: dict, product_code: str):
        trades = [
            BitflyerTrades(
                product_code=product_code,
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

    async def _handle_depth(self, data: dict, product_code: str):
        # don't need sorted asks or bids
        depth = BitflyerDepth(
            product_code=product_code,
            **data['params']['message']
        )
