"""
author: thomaszdxsn
"""
import pytest

from src.schemas.regexes import *


@pytest.mark.parametrize('raw,result', [
    ('ok_sub_spot_ltc_btc_ticker',
     {'base': 'ltc', 'quote': 'btc', 'data_type': 'ticker'}),
    ('ok_sub_spot_ltc_usdt_deals',
     {'base': 'ltc', 'quote': 'usdt', 'data_type': 'deals'}),
    ('ok_sub_spot_ltc_usdt_depth_20',
     {'base': 'ltc', 'quote': 'usdt', 'data_type': 'depth_20'}),
    ('ok_sub_spot_bch_usdt_kline_1min',
     {'base': 'bch', 'quote': 'usdt', 'data_type': 'kline_1min'})
])
def test_okex_spot_ws_channels_re_patterns(raw, result):
    match_result = OKEX_SPOT_WS_CHANS.match(raw).groupdict()
    assert match_result == result


@pytest.mark.parametrize('raw,result', [
    ('ok_sub_futureusd_etc_ticker_quarter',
     {'symbol': 'etc', 'data_type': 'ticker', 'contract_type': 'quarter'}),
    ('ok_sub_futureusd_etc_ticker_this_week',
     {'symbol': 'etc', 'data_type': 'ticker', 'contract_type': 'this_week'}),
    ('ok_sub_futureusd_ltc_depth_quarter_20',
     {'symbol': 'ltc', 'data_type': 'depth', 'contract_type': 'quarter'}),
    ('ok_sub_futureusd_etc_depth_this_week_20',
     {'symbol': 'etc', 'data_type': 'depth', 'contract_type': 'this_week'}),
    ('ok_sub_futureusd_btg_kline_next_week_1min',
     {'symbol': 'btg', 'data_type': 'kline', 'contract_type': 'next_week'}),
    ('ok_sub_futureusd_btg_kline_quarter_1min',
     {'symbol': 'btg', 'data_type': 'kline', 'contract_type': 'quarter'}),
    ('ok_sub_futureusd_btg_trade_quarter',
     {'symbol': 'btg', 'data_type': 'trade', 'contract_type': 'quarter'})
])
def test_okex_future_ws_channels_re_patterns(raw, result):
    match_result = OKEX_FUTURE_WS_CHANS.match(raw).groupdict()
    assert match_result == result