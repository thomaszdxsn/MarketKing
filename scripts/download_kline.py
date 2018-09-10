"""
author: thomaszdxsn
"""
from src.sdk import *

import arrow
import pandas as pd


def main():
    orig_start_time = arrow.utcnow().shift(years=-1)
    start_time = orig_start_time.timestamp * 1000
    rest_sdk = BinanceRest()
    kline_list = []
    last_end = None
    while 1:
        if last_end and last_end == start_time:
            save_file(kline_list)
            break
        print('下载 {}'.format(start_time))
        data = rest_sdk.get_kline('btcusdt', '1h', start_time=start_time)
        last_end = start_time
        if data.error != 0 or not data.data:
            print("出现错误或者爬取完毕")
            save_file(kline_list)
            break
        else:
            kline_list.extend(
                {
                    'start_time': item[0],
                    'open': item[1],
                    'high': item[2],
                    'low': item[3],
                    'close': item[4],
                    'vol': item[5],
                    'quote_vol': item[7],
                    'trades_num': item[8],
                    'taker_buy_base_asset_vol': item[9],
                    'taker_buy_quote_asset_vol': item[10]

                 }
                for item in data.data
            )
            start_time = data.data[-1][0]


def save_file(data):
    df = pd.DataFrame(data)
    df.to_csv('btc_kline_from_binance.csv', index=False)

main()