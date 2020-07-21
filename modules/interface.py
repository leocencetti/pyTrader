###
# File created by Leonardo Cencetti on 7/20/20
###
import logging
from threading import Thread

from modules.databus import Topic
from support.alpha_vantage_api import AlphaVantage
from support.types import StockRequest


class Interface:
    def __init__(self, task_bus, data_bus):
        # I/O handles
        self._input_bus: Topic = task_bus
        self._output_bus: Topic = data_bus
        # support
        self._logger = logging.getLogger(__name__)
        self._sig_interrupt = False
        self._running = False
        # main
        self.source = AlphaVantage()
        self.thread = Thread(target=self._routine)
        self.thread.daemon = True

    def run(self, join=False):
        if self._running:
            self._logger.warning('Thread already running.')
            return
        # start the thread
        self._sig_interrupt = False
        self.thread.start()

        self._logger.debug('Thread started.')
        if join:
            self._logger.debug('Joining thread.')
            self.thread.join()

    def stop(self):
        if not self._running:
            self._logger.warning('Thread not running.')
            return
        # stopping thread
        self._logger.debug('Stopping thread.')
        self._sig_interrupt = True
        self.thread.join()
        self._running = False
        self._logger.debug('Thread stopped.')

    def _routine(self):
        while not self._sig_interrupt:
            self._run_once()

        self._logger.debug('Thread loop interrupted.')

    def _run_once(self):
        task: StockRequest = self._input_bus.get()
        data = self.source.process_stock_request(task)
        self._input_bus.task_done()
        self._output_bus.put(data)

    def close(self):
        self.stop()
