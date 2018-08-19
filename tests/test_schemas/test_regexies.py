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


@pytest.mark.parametrize('raw,result', [
    ('etcusdt@kline_1m',
     {'symbol': 'etcusdt', 'data_type': 'kline_1m'}),
    ('bnbbtc@depth20',
     {'symbol': 'bnbbtc', 'data_type': 'depth20'}),
    ('eoseth@ticker',
     {'symbol': 'eoseth', 'data_type': 'ticker'}),
    ('bccusdt@trade',
     {'symbol': 'bccusdt', 'data_type': 'trade'})
])
def test_binance_ws_channels_re_patterns(raw, result):
    match_result = BINANCE_WS_CHANS.match(raw).groupdict()
    assert match_result == result


@pytest.mark.parametrize('raw,result', [
    ('market.btcusdt.detail',
     {'symbol': 'btcusdt', 'data_type': 'detail'}),
    ('market.btcusdt.depth.step0',
     {'symbol': 'btcusdt', 'data_type': 'depth'}),
    ('market.btcusdt.kline.1min',
     {'symbol': 'btcusdt', 'data_type': 'kline'}),
    ('market.btcusdt.trade.detail',
     {'symbol': 'btcusdt', 'data_type': 'trade'})
])
def test_huobi_ws_channels_re_patterns(raw, result):
    match_result = HUOBI_WS_CHANS.match(raw).groupdict()
    assert match_result == result



@pytest.mark.parametrize('raw,result', [
    ('lightning_ticker_FX_BTC_JPY',
     {'data_type': 'ticker', 'product_code': 'FX_BTC_JPY'}),
    ('lightning_ticker_BTCJPY28SEP2018',
     {'data_type': 'ticker', 'product_code': 'BTCJPY28SEP2018'}),
    ('lightning_executions_FX_BTC_JPY',
     {'data_type': 'executions', 'product_code': 'FX_BTC_JPY'}),
    ('lightning_board_snapshot_BTC_JPY',
     {'data_type': 'board_snapshot', 'product_code': 'BTC_JPY'})
])
def test_bitflyer_ws_channels_re_patterns(raw, result):
    match_result = BITFLYER_WS_CHANS.match(raw).groupdict()
    assert match_result == result


@pytest.mark.parametrize('raw,result', [
    ('ticker.ltcusdt',
     {'data_type': 'ticker', 'symbol': 'ltcusdt'}),
    ('depth.L20.btcusdt',
     {'data_type': 'depth', 'symbol': 'btcusdt'}),
    ('candle.M1.ethusdt',
     {'data_type': 'candle', 'symbol': 'ethusdt'}),
    ('trade.btcusdt',
     {'data_type': 'trade', 'symbol': 'btcusdt'})
])
def test_fcoin_ws_channels_re_patterns(raw, result):
    match_result = FCOIN_WS_CHANS.match(raw).groupdict()
    assert match_result == result