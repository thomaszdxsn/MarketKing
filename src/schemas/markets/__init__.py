"""
author: thomaszdxsn
"""

from .. import DataClassAbstract


class MarketItemBase(DataClassAbstract):

    def get_unique_indexes(self):
        return None



from .depth import *
from .ticker import *
from .trades import *
from .kline import *
from ._bitmex import *