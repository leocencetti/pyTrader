###
# File created by Leonardo Cencetti on 7/20/20
###
from dataclasses import dataclass

import pandas as pd


@dataclass
class StockBase:
    symbol: str
    type: str
    interval: str


@dataclass
class StockRequest(StockBase):
    # key: str
    pass


@dataclass
class StockResponse(StockBase):
    data: pd.DataFrame
