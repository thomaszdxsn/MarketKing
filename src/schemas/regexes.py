"""
Author: thomaszdxsn
"""
import re

##########################
# okex_spot ##############
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