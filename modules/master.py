###
# File created by Leonardo Cencetti on 7/19/20
###
from dataclasses import dataclass
from queue import Queue

from config.config import *
from modules.interface import Interface
from modules.processor import Processor


@dataclass
class Architecture:
    interface: Interface
    processor: Processor

    def __getitem__(self, item):
        return list(vars(self).values())[item]


stock_list = []


class Master:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._running = False
        self.data_topic = Queue()
        self.out_topic = Queue()
        # instantiate modules
        self.modules = Architecture(
            interface=Interface(output_bus=self.data_topic),
            processor=Processor(input_bus=self.data_topic, output_bus=self.out_topic)
        )

    def run(self):
        if self._running:
            self._logger.warning('Module already running.')
            return
        self._logger.info('Starting all modules.')
        for mod in self.modules:
            mod.start()
        self._running = True
        self.modules.processor.join()

    def close(self):
        if not self._running:
            self._logger.warning('Module not running.')
            return
        self._logger.info('Closing all modules.')
        for mod in self.modules:
            mod.close()

    def stop(self):
        if not self._running:
            self._logger.warning('Module not running.')
            return
        self._logger.info('Stopping all modules.')
        for mod in self.modules:
            mod.stop()
