###
# File created by Leonardo Cencetti on 3/31/20
###
from threading import Thread
from time import sleep

from support.alpha_vantage_api import get_intraday, get_ema, get_sma


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
            task = self.queue.get()
            if task is None:
                break

            try:
                self._execute_task(task)
                self.queue.task_done()

            except ValueError:
                print('[{0: <9}] Caught exception, retrying!'.format(self._T.name))
                self.queue.task_done()
                self.queue.put(task)
            finally:
                sleep(self._interval)

    def _execute_task(self, task):
        key = task['key']
        symbol = task['symbol']
        series_type = 'close'
        if task['task_type'] == 'sma50':
            data = get_sma(symbol=symbol, key=key, interval='1min', time_period=50, series_type=series_type)
        elif task['task_type'] == 'sma200':
            data = get_sma(symbol=symbol, key=key, interval='1min', time_period=200, series_type=series_type)
        elif task['task_type'] == 'ema50':
            data = get_ema(symbol=symbol, key=key, interval='1min', time_period=50, series_type=series_type)
        elif task['task_type'] == 'ema200':
            data = get_ema(symbol=symbol, key=key, interval='1min', time_period=200, series_type=series_type)
        elif task['task_type'] == 'intraday':
            data = get_intraday(symbol, key)
        elif task['task_type'] == 'full_intraday':
            data = get_intraday(symbol, key, outputsize='full')
        else:
            print('[{0: <9}] Unknown task type!'.format(self._T.name))
            return
        self.data.put(data)

    def join(self):
        self._T.join()
