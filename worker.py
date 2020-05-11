###
# File created by Leonardo Cencetti on 3/31/20
###
from threading import Thread
from time import sleep

from alpha_vantage_fork.alpha_vantage.techindicators import TechIndicators
from alpha_vantage_fork.alpha_vantage.timeseries import TimeSeries


def get_intraday(symbol, key):
    ts = TimeSeries(key, output_format='pandas')
    intraday, _ = ts.get_intraday(symbol=symbol, interval='1min', outputsize='compact')
    return intraday


def get_sma(symbol, key):
    ti = TechIndicators(key, output_format='pandas')
    sma, _ = ti.get_sma(symbol=symbol, interval='1min')
    return sma


class Worker:
    def __init__(self, taskQueue, dataQueue, interval=12):
        self.queue = taskQueue
        self.data = dataQueue
        self._T = None
        self._interval = interval

    def run(self):
        self._T = Thread(target=self.get_data)
        self._T.daemon = True
        self._T.start()

    def get_data(self):
        while True:
            item = self.queue.get()
            if item is None:
                break
            key = item['key']
            symbol = item['symbol']
            try:
                data = get_intraday(symbol, key)
                sma = get_sma(symbol, key)
                self.data.put((symbol, data))
                self.queue.task_done()

            except ValueError:
                print('[{0: <9}] Caught exception, retrying!'.format(self._T.name))
                self.queue.task_done()
                self.queue.put(item)
            finally:
                sleep(self._interval)

    def join(self):
        self._T.join()
