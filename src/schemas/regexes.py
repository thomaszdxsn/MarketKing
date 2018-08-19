"""
Author: thomaszdxsn
"""
import re

##########################
# okex ###################
##########################

OKEX_SPOT_WS_CHANS = re.compile(
    """
    ok_sub_spot_
    (?P<base>[a-z]+)_
    (?P<quote>[a-z]+)_
    (?P<data_type>\w+)
    """,
    flags=re.VERBOSE|re.IGNORECASE
)

OKEX_FUTURE_WS_CHANS = re.compile(
    """
    ok_sub_futureusd_
    (?P<symbol>[a-z]+)_
    (?P<data_type>[a-z]+)_
    (?P<contract_type>[a-z]+(_[a-z]+)*)         # this_week|next_week|quarter
    (_[a-z0-9]+)?
    """,
    flags=re.VERBOSE|re.IGNORECASE
)

##########################
# binance ################
##########################

BINANCE_WS_CHANS = re.compile(
    """
    (?P<symbol>[a-z]+)@
    (?P<data_type>\w+)
    """,
    flags=re.VERBOSE|re.IGNORECASE
)

##########################
# huobi ##################
##########################

HUOBI_WS_CHANS = re.compile(
    """
    market\.
    (?P<symbol>[a-z]+)\.
    (?P<data_type>[a-z]+)
    (\.\w+)?
    """,
    flags=re.VERBOSE|re.IGNORECASE
)

##########################
# bitflyer ###############
##########################

BITFLYER_WS_CHANS = re.compile(
    """
    lightning_
    (?P<data_type>[a-z0-9_]+)_
    (?P<product_code>[A-Z0-9_]+)
    """,
    flags=re.VERBOSE
)

##########################
# fcoin ##################
##########################

FCOIN_WS_CHANS = re.compile(
    """
    (?P<data_type>[a-z]+)\.
    (\w+\.)?
    (?P<symbol>[a-z]+)
    """,
    flags=re.VERBOSE|re.IGNORECASE
)


##########################
# cointiger ##################
##########################

COINTIGER_WS_CHANS = re.compile(
    """
    market_
    (?P<symbol>[a-z]+)_
    (?P<data_type>[a-z]+)
    (_\w+)?
    """,
    flags=re.VERBOSE|re.IGNORECASE
)