###
# File created by Leonardo Cencetti on 7/23/20
###
from logging import Logger
from threading import Thread

from modules.databus import Topic


class BaseModule:
    def __init__(self, input_bus, output_bus):
        # I/O handles
        self._input_bus: Topic = input_bus
        self._output_bus: Topic = output_bus
        # support
        self._logger = None
        self._sig_interrupt = False
        self._running = False
        # main
        self.thread = Thread(target=self._routine, daemon=True)

    def _routine(self):
        while not self._sig_interrupt:
            self._run_once()
        self._logger.debug('Module loop interrupted.')

    def _run_once(self):
        pass

    def run(self, join=False):
        if self._running:
            self._logger.warning('Module already running.')
            return
        # start the thread
        self._sig_interrupt = False
        self.thread.start()

        self._logger.debug('Module started.')
        if join:
            self._logger.debug('Joining thread.')
            self.thread.join()

    def stop(self):
        if not self._running:
            self._logger.warning('Module not running.')
            return
        # stopping thread
        self._logger.debug('Stopping thread.')
        self._sig_interrupt = True
        self.thread.join()
        self._running = False
        self._logger.debug('Thread stopped.')

    def close(self):
        self.stop()
