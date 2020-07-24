###
# File created by Leonardo Cencetti on 7/19/20
###
import logging
import random
import string

import pandas as pd

from external.alphavantage.alpha_vantage.techindicators import TechIndicators
from external.alphavantage.alpha_vantage.timeseries import TimeSeries
from support.types import StockRequest


class AlphaVantage:
    """
    Facade around the AlphaVantage API
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def process_stock_request(self, stock_req: StockRequest):
        """
        Processes a stock request
        :param stock_req: equity data request
        :return:
        """
        data = self._api_call(stock_req.type, stock_req.symbol, stock_req.interval)
        return data

    def combo_request(self, symbol, type_list, interval):
        data = pd.DataFrame()
        for t in type_list:
            data = data.join(self._api_call(t, symbol, interval), how='outer')
        data.insert(0, 'symbol', symbol)
        return data

    def _api_call(self, t_type, symbol, interval):
        """
        Determines which sub-function to call based on the parameters
        :param t_type: task type, supported values are 'sma50', 'sma200', 'ema50', 'ema200', 'intraday', 'full_intraday'
        :param symbol: the symbol for the equity we want to get its data
        :param interval: time interval between two consecutive values, supported values are
        '1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly' (default 'daily')
        """
        key = key_generator()
        if t_type == 'sma50':
            data = self.get_sma(symbol=symbol, key=key, interval=interval, time_period=50)
        elif t_type == 'sma200':
            data = self.get_sma(symbol=symbol, key=key, interval=interval, time_period=200)
        elif t_type == 'ema50':
            data = self.get_ema(symbol=symbol, key=key, interval=interval, time_period=50)
        elif t_type == 'ema200':
            data = self.get_ema(symbol=symbol, key=key, interval=interval, time_period=200)
        elif t_type == 'intraday':
            data = self.get_intraday(symbol, key)
        elif t_type == 'full_intraday':
            data = self.get_intraday(symbol, key, output_size='full')
        else:
            self._logger.warning('Request type "{}" not valid'.format(t_type))
            return
        return data

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
