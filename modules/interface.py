###
# File created by Leonardo Cencetti on 7/20/20
###
import logging
from threading import Thread

from modules.base import BaseModule
from support.alpha_vantage_api import AlphaVantage

symbol_list = ['AAPL', 'MSFT']
data_type_list = ['intraday']


class Interface(BaseModule):
    def __init__(self, output_bus):
        super().__init__(None, output_bus)
        self._logger = logging.getLogger(__name__)
        # main
        self.source = AlphaVantage()

    def _run_once(self):
        threads = []
        for sym in symbol_list:
            threads.append(Thread(target=self._sub_task, args=[sym], daemon=True))
            threads[-1].start()
        for T in threads:
            T.join()

    def _sub_task(self, symbol):
        data = self.source.combo_request(symbol, data_type_list, '1min')
        self._output_bus.put(data.tail(10))
