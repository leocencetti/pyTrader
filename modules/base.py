###
# File created by Leonardo Cencetti on 7/23/20
###
import datetime as dt
from queue import Queue
from threading import Thread, Event

from config.config import loop_interval


class BaseModule:
    def __init__(self, input_bus: Queue, output_bus: Queue):
        # I/O handles
        self._input_bus = input_bus
        self._output_bus = output_bus
        # support
        self._logger = None
        self._sig_interrupt = Event()
        self._running = False

        # main
        self.interval: dt.timedelta = loop_interval
        self._last_run = dt.datetime.now()
        self.thread = Thread(target=self._routine, daemon=True)

    def _routine(self):
        while not self._sig_interrupt.is_set():
            time = dt.datetime.now()
            if time - self._last_run >= self.interval:
                self._last_run = time
                self._run_once()

        self._logger.debug('Module loop interrupted.')

    def _run_once(self):
        pass

    def start(self, join=False):
        """
        Starts the module thread
        :param bool join: wait for the thread to complete
        """
        if self._running:
            self._logger.warning('Module already running.')
            return
        # start the thread
        self._sig_interrupt.clear()
        self.thread.start()
        self._running = True
        self._logger.info('Module started.')
        if join:
            self._logger.debug('Joining thread.')
            self.thread.join()

    def stop(self):
        """
        Stops the module thread
        """
        if not self._running:
            self._logger.warning('Module not running.')
            return
        # stopping thread
        self._logger.debug('Stopping Module.')
        self._sig_interrupt.set()
        if self.thread.is_alive():
            self.thread.join()
        self._running = False
        self._logger.info('Module stopped.')

    close = stop
