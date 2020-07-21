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

        self.bus = BusManager() \
            .add_topic(RAW_REQ_BUS) \
            .add_topic(RAW_DATA_BUS) \
            .add_topic(DB_REQ_BUS) \
            .add_topic(DB_DATA_BUS)
        # instantiate modules
        self.modules = Architecture(
            broker=Broker(),
            dashboard=Dashboard(),
            interface=Interface(
                task_bus=self.bus.get_topic(RAW_REQ_BUS),
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

        import datetime as dt
        import pandas as pd
        from support.types import StockResponse
        msg = StockResponse(symbol='GOOG', type='intraday', interval='1min', data=pd.DataFrame(),
                            timestamp=dt.datetime.now())
        self.modules.storage.store_data(msg)
        self.modules.processor.join()

    def close(self):
        self._logger.info('Closing all modules.')
        for mod in self.modules:
            mod.close()

    def stop(self):
        self._logger.info('Stopping all modules.')
        for mod in self.modules:
            mod.stop()
