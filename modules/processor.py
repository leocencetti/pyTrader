###
# File created by Leonardo Cencetti on 7/19/20
###

import logging

from modules.base import BaseModule


class Processor(BaseModule):
    def __init__(self, input_bus, output_bus):
        super().__init__(input_bus, output_bus)
        self._logger = logging.getLogger(__name__)

    def _run_once(self):
        while not self._input_bus.empty():
            data = self._input_bus.get(timeout=2 * self.interval.seconds)
            print(data)

    def join(self):
        while True:
            pass
