###
# File created by Leonardo Cencetti on 7/19/20
###
from external.alphavantage.alpha_vantage.techindicators import TechIndicators
from external.alphavantage.alpha_vantage.timeseries import TimeSeries


def get_intraday(symbol, key, interval='1min', outputsize='compact'):
    ts = TimeSeries(key, output_format='pandas')
    data, meta = ts.get_intraday(symbol=symbol, interval=interval, outputsize=outputsize)
    data.reset_index(inplace=True)
    data.rename(columns={
        '1. open'  : 'open',
        '2. high'  : 'high',
        '3. low'   : 'low',
        '4. close' : 'close',
        '5. volume': 'volume'
    }, inplace=True)
    # data = data.melt(['date'], var_name="subtype")
    data.insert(1, 'time zone', meta['6. Time Zone'])
    data.insert(2, 'symbol', symbol)
    data.insert(3, 'frequency', interval)
    data.insert(4, 'type', 'intraday')
    return data


def get_sma(symbol, key, interval='1min', time_period=200, series_type='close'):
    ti = TechIndicators(key, output_format='pandas')
    data, meta = ti.get_sma(symbol=symbol, interval=interval, time_period=time_period, series_type=series_type)
    data.reset_index(inplace=True)
    data.rename(columns={
        'SMA': str(time_period)
    }, inplace=True)
    # data = data.melt(['date'], var_name="subtype")
    data.insert(1, 'time zone', meta['7: Time Zone'])
    data.insert(2, 'symbol', symbol)
    data.insert(3, 'frequency', interval)
    data.insert(4, 'type', 'sma')
    return data


def get_ema(symbol, key, interval='1min', time_period=200, series_type='close'):
    ti = TechIndicators(key, output_format='pandas')
    data, meta = ti.get_ema(symbol=symbol, interval=interval, time_period=time_period, series_type=series_type)
    data.reset_index(inplace=True)
    data.rename(columns={
        'EMA': str(time_period)
    }, inplace=True)
    # data = data.melt(['date'], var_name="subtype")
    data.insert(1, 'time zone', meta['7: Time Zone'])
    data.insert(2, 'symbol', symbol)
    data.insert(3, 'frequency', interval)
    data.insert(4, 'type', 'ema')
    return data
