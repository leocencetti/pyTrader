###
# File created by Leonardo Cencetti on 3/31/20
###
from threading import Thread
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from time import sleep


class Worker:
    def __init__(self, queue, data, interval=12):
        self.queue = queue
        self.data = data
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
            ts = TimeSeries(key, output_format='pandas')
            ti = TechIndicators(key, output_format='pandas')
            try:
                data, meta_data = ts.get_daily(symbol=symbol)
                # sma, meta_sma = ti.get_sma(symbol=symbol)
                self.queue.task_done()
                print('[Thread {}] Successful call'.format(round(self._T.ident % 1e4)))

            except ValueError:
                print('[Thread {}] Catched exception!'.format(round(self._T.ident % 1e4)))
                self.queue.task_done()
                self.queue.put(item)
            finally:
                sleep(self._interval)

    def join(self):
        self._T.join()
