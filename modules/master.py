###
# File created by Leonardo Cencetti on 7/19/20
###
from dataclasses import dataclass

from config.config import *
from modules.broker import Broker
from modules.dashboard import Dashboard
from modules.databus import BusManager
from modules.interface import Interface
from modules.logger import Logger
from modules.processor import Processor
from modules.storage import Storage


@dataclass
class Architecture:
    broker: Broker
    dashboard: Dashboard
    interface: Interface
    logger: Logger
    processor: Processor
    storage: Storage

    def __getitem__(self, item):
        return list(vars(self).values())[item]

stock_list = []

class Master:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._running = False

        self.bus = BusManager() \
            .add_topic(RAW_REQ_BUS) \
            .add_topic(RAW_DATA_BUS) \
            .add_topic(DB_REQ_BUS) \
            .add_topic(DB_RES_BUS)
        # instantiate modules
        self.modules = Architecture(
            broker=Broker(),
            dashboard=Dashboard(),
            interface=Interface(
                input_bus=self.bus.get_topic(RAW_REQ_BUS),
                output_bus=self.bus.get_topic(RAW_DATA_BUS)
            ),
            logger=Logger(),
            processor=Processor(
                input_bus=self.bus.get_topic(DB_REQ_BUS),
                output_bus=self.bus.get_topic(DB_RES_BUS),
                stock_list=stock_list
            ),
            storage=Storage(
                input_bus=self.bus.get_topic(DB_REQ_BUS),
                output_bus=self.bus.get_topic(DB_RES_BUS)
            )
        )

    def run(self):
        if self._running:
            self._logger.warning('Module already running.')
            return
        self._logger.info('Starting all modules.')
        for mod in self.modules:
            mod.run()
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
