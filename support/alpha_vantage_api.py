###
# File created by Leonardo Cencetti on 7/19/20
###
import datetime as dt
import logging
import random
import string

from external.alphavantage.alpha_vantage.techindicators import TechIndicators
from external.alphavantage.alpha_vantage.timeseries import TimeSeries
from support.types import StockResponse


class AlphaVantage:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def process_stock_request(self, stock_req):
        key = key_generator()
        if stock_req.type == 'sma50':
            data = self.get_sma(symbol=stock_req.symbol, key=key, interval=stock_req.interval, time_period=50)
        elif stock_req.type == 'sma200':
            data = self.get_sma(symbol=stock_req.symbol, key=key, interval=stock_req.interval, time_period=200)
        elif stock_req.type == 'ema50':
            data = self.get_ema(symbol=stock_req.symbol, key=key, interval=stock_req.interval, time_period=50)
        elif stock_req.type == 'ema200':
            data = self.get_ema(symbol=stock_req.symbol, key=key, interval=stock_req.interval, time_period=200)
        elif stock_req.type == 'intraday':
            data = self.get_intraday(stock_req.symbol, key)
        elif stock_req.type == 'full_intraday':
            data = self.get_intraday(stock_req.symbol, key, output_size='full')
        else:
            self._logger.warning('Request type "{}" not valid'.format(stock_req.type))
            return

        message = StockResponse(
            timestamp=dt.datetime.now(),
            symbol=stock_req.symbol,
            interval=stock_req.interval,
            type=stock_req.type,
            data=data
        )
        return message

    @staticmethod
    def get_intraday(symbol, key, interval='1min', output_size='compact'):
        ts = TimeSeries(key, output_format='pandas')
        data, meta = ts.get_intraday(symbol=symbol, interval=interval, outputsize=output_size)
        data.rename(columns={
            '1. open'  : 'open',
            '2. high'  : 'high',
            '3. low'   : 'low',
            '4. close' : 'close',
            '5. volume': 'volume'
        }, inplace=True)
        return data

    @staticmethod
    def get_sma(symbol, key, interval='1min', time_period=200, series_type='close'):
        ti = TechIndicators(key, output_format='pandas')
        data, meta = ti.get_sma(symbol=symbol, interval=interval, time_period=time_period, series_type=series_type)
        data.rename(columns={
            'SMA': 'SMA{}'.format(time_period)
        }, inplace=True)
        return data

    @staticmethod
    def get_ema(symbol, key, interval='1min', time_period=200, series_type='close'):
        ti = TechIndicators(key, output_format='pandas')
        data, meta = ti.get_ema(symbol=symbol, interval=interval, time_period=time_period, series_type=series_type)
        data.rename(columns={
            'EMA': 'EMA{}'.format(time_period)
        }, inplace=True)
        return data


def key_generator(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
