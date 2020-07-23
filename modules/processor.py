###
# File created by Leonardo Cencetti on 7/19/20
###
import datetime as dt

from modules.base import BaseModule
from support.types import StockRequest
import logging

class Processor(BaseModule):
    def __init__(self, input_bus, output_bus, stock_list):
        super().__init__(input_bus, output_bus)
        self._logger = logging.getLogger(__name__)
        self.stock_list = stock_list

    def _run_once(self):
        for sym in self.stock_list:
            self._create_request(sym, '1min', 'sma50')

    def _create_request(self, symbol, interval, type):
        message = StockRequest(
            timestamp=dt.datetime.now(),
            symbol=symbol,
            interval=interval,
            type=type
        )
        self._output_bus.put(message)

    def join(self):
        while True:
            pass
