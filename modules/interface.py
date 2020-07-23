###
# File created by Leonardo Cencetti on 7/20/20
###
import logging

from modules.base import BaseModule
from support.alpha_vantage_api import AlphaVantage


class Interface(BaseModule):
    def __init__(self, input_bus, output_bus):
        super().__init__(input_bus, output_bus)
        self._logger = logging.getLogger(__name__)
        # main
        self.source = AlphaVantage()

    def _run_once(self):
        task = self._input_bus.get()
        data = self.source.process_stock_request(task)
        self._input_bus.task_done()
        self._output_bus.put(data)

