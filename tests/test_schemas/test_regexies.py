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

