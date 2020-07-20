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


class Master:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        # instantiate modules
        self.bus = BusManager() \
            .add_topic(DATA_REQ_BUS) \
            .add_topic(RAW_DATA_BUS)

        self.modules = Architecture(
            broker=Broker(),
            dashboard=Dashboard(),
            interface=Interface(
                task_bus=self.bus.get_topic(DATA_REQ_BUS),
                data_bus=self.bus.get_topic(RAW_DATA_BUS)
            ),
            logger=Logger(),
            processor=Processor(),
            storage=Storage(),
        )

    def run(self):
        self._logger.info('Starting all modules.')
        for mod in self.modules:
            mod.run()

    def close(self):
        self._logger.info('Closing all modules.')
        for mod in self.modules:
            mod.close()

    def stop(self):
        self._logger.info('Stopping all modules.')
        for mod in self.modules:
            mod.stop()


def main():
    master = Master()
    master.run()


if __name__ == '__main__':
    main()
