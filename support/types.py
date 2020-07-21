###
# File created by Leonardo Cencetti on 7/20/20
###
import datetime as dt
from dataclasses import dataclass

import pandas as pd


@dataclass
class Message:
    timestamp: dt.datetime


@dataclass
class StockBase(Message):
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


@dataclass
class DbRequest(StockBase):
    pass


@dataclass
class DbResponse(StockBase):
    data: pd.DataFrame
