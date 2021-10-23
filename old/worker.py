###
# File created by Leonardo Cencetti on 3/31/20
###
from threading import Thread
from time import sleep

from alpha_vantage_fork.alpha_vantage.techindicators import TechIndicators
from alpha_vantage_fork.alpha_vantage.timeseries import TimeSeries


def get_intraday(symbol, key, interval="1min", outputsize="compact"):
    ts = TimeSeries(key, output_format="pandas")
    data, meta = ts.get_intraday(
        symbol=symbol, interval=interval, outputsize=outputsize
    )
    data.reset_index(inplace=True)
    data.rename(
        columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume",
        },
        inplace=True,
    )
    data = data.melt(["date"], var_name="subtype")
    data.insert(1, "time zone", meta["6. Time Zone"])
    data.insert(2, "symbol", symbol)
    data.insert(3, "frequency", interval)
    data.insert(4, "type", "intraday")
    return data


def get_sma(symbol, key, interval="1min", time_period=200, series_type="close"):
    ti = TechIndicators(key, output_format="pandas")
    data, meta = ti.get_sma(
        symbol=symbol,
        interval=interval,
        time_period=time_period,
        series_type=series_type,
    )
    data.reset_index(inplace=True)
    data.rename(columns={"SMA": str(time_period)}, inplace=True)
    data = data.melt(["date"], var_name="subtype")
    data.insert(1, "time zone", meta["7: Time Zone"])
    data.insert(2, "symbol", symbol)
    data.insert(3, "frequency", interval)
    data.insert(4, "type", "sma")
    return data


def get_ema(symbol, key, interval="1min", time_period=200, series_type="close"):
    ti = TechIndicators(key, output_format="pandas")
    data, meta = ti.get_ema(
        symbol=symbol,
        interval=interval,
        time_period=time_period,
        series_type=series_type,
    )
    data.reset_index(inplace=True)
    data.rename(columns={"EMA": str(time_period)}, inplace=True)
    data = data.melt(["date"], var_name="subtype")
    data.insert(1, "time zone", meta["7: Time Zone"])
    data.insert(2, "symbol", symbol)
    data.insert(3, "frequency", interval)
    data.insert(4, "type", "ema")
    return data


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
                print("[{0: <9}] Caught exception, retrying!".format(self._T.name))
                self.queue.task_done()
                self.queue.put(task)
            finally:
                sleep(self._interval)

    def _execute_task(self, task):
        key = task["key"]
        symbol = task["symbol"]
        series_type = "close"
        if task["task_type"] == "sma50":
            data = get_sma(
                symbol=symbol,
                key=key,
                interval="1min",
                time_period=50,
                series_type=series_type,
            )
        elif task["task_type"] == "sma200":
            data = get_sma(
                symbol=symbol,
                key=key,
                interval="1min",
                time_period=200,
                series_type=series_type,
            )
        elif task["task_type"] == "ema50":
            data = get_ema(
                symbol=symbol,
                key=key,
                interval="1min",
                time_period=50,
                series_type=series_type,
            )
        elif task["task_type"] == "ema200":
            data = get_ema(
                symbol=symbol,
                key=key,
                interval="1min",
                time_period=200,
                series_type=series_type,
            )
        elif task["task_type"] == "intraday":
            data = get_intraday(symbol, key)
        elif task["task_type"] == "fintraday":
            data = get_intraday(symbol, key, outputsize="full")
        else:
            print("[{0: <9}] Unknown task type!".format(self._T.name))
            return
        self.data.put(data)

    def join(self):
        self._T.join()
