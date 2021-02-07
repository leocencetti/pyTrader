###
# File created by Leonardo Cencetti on 2/6/21
###
from dataclasses import dataclass

import pandas as pd
import pytz

from external.alphavantage.alpha_vantage.techindicators import TechIndicators
from external.alphavantage.alpha_vantage.timeseries import TimeSeries
from nodes.common import CustomEnum


class RequestType(CustomEnum):
    SMA50 = 'sma50'
    SMA200 = 'sma200'
    EMA50 = 'ema50'
    EMA200 = 'ema200'
    INTRADAY = 'compact_intraday'
    FULL_INTRADAY = 'full_intraday'


class SeriesType(CustomEnum):
    CLOSE = 'close'
    OPEN = 'open'
    HIGH = 'high'
    LOW = 'low'
    VOLUME = 'volume'
    ALL = 'all'


class Interval(CustomEnum):
    MIN1 = '1min'
    MIN5 = '5min'
    MIN15 = '15min'
    MIN30 = '30min'
    HOUR = '60min'
    DAY = 'daily'
    WEEK = 'weekly'
    MONTH = 'monthly'


@dataclass
class AVRequest:
    key: str
    type: RequestType
    interval: Interval
    symbol: str
    series: SeriesType


@dataclass
class AVReply:
    type: RequestType
    interval: Interval
    symbol: str
    series: SeriesType
    data: pd.DataFrame
    timezone: pytz.timezone


def get_intraday(symbol, key, interval='1min', outputsize='compact'):
    ts = TimeSeries(key, output_format='pandas')
    data, meta = ts.get_intraday(symbol=symbol, interval=interval, outputsize=outputsize)
    data.rename(columns={
        '1. open'  : 'open',
        '2. high'  : 'high',
        '3. low'   : 'low',
        '4. close' : 'close',
        '5. volume': 'volume'
    }, inplace=True)
    return AVReply(type=RequestType('{}_intraday'.format(outputsize)),
                   interval=Interval(interval),
                   symbol=symbol,
                   series=SeriesType.ALL,
                   data=data,
                   timezone=pytz.timezone(meta['6. Time Zone']))


def get_sma(symbol, key, interval='1min', time_period=200, series_type='close'):
    ti = TechIndicators(key, output_format='pandas')
    data, meta = ti.get_sma(symbol=symbol, interval=interval, time_period=time_period, series_type=series_type)
    data.rename(columns={
        'SMA': 'sma{}'.format(time_period)
    }, inplace=True)
    return AVReply(type=RequestType('sma{}'.format(time_period)),
                   interval=Interval(interval),
                   symbol=symbol,
                   series=SeriesType(series_type),
                   data=data,
                   timezone=pytz.timezone(meta['7: Time Zone']))


def get_ema(symbol, key, interval='1min', time_period=200, series_type='close'):
    ti = TechIndicators(key, output_format='pandas')
    data, meta = ti.get_ema(symbol=symbol, interval=interval, time_period=time_period, series_type=series_type)
    data.rename(columns={
        'EMA': 'ema{}'.format(time_period)
    }, inplace=True)
    return AVReply(type=RequestType('ema{}'.format(time_period)),
                   interval=Interval(interval),
                   symbol=symbol,
                   series=SeriesType(series_type),
                   data=data,
                   timezone=pytz.timezone(meta['7: Time Zone']))
