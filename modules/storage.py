###
# File created by Leonardo Cencetti on 7/19/20
###
import os
import sqlite3
from sqlite3 import Error
from threading import Thread
import datetime as dt
import pandas as pd

from config.config import *
from modules.databus import Topic
from support.types import DbRequest, StockResponse


class Storage:
    def __init__(self, request_bus, response_bus):
        # I/O handles
        self._input_bus: Topic = request_bus
        self._output_bus: Topic = response_bus
        # support
        self._logger = logging.getLogger(__name__)
        self._sig_interrupt = False
        self._running = False
        # main
        self.thread = Thread(target=self._routine)
        self.thread.daemon = True
        self._connection = None
        self._cursor = None

    def _connect(self):
        """ Create a database connection to the master database. """
        try:
            self._connection = sqlite3.connect(DB_PATH)
            self._cursor = self._connection.cursor()
            self._logger.info('Connected to database "{}"'.format(DB_PATH))
        except Error as e:
            self._logger.error(e)

    def _disconnect(self):
        """ Disconnects from master database. """
        if self._connection:
            self._cursor.close()
            self._connection.close()
            self._logger.info('Disconnected from database "{}"'.format(DB_PATH))
        else:
            self._logger.warning('Database not connected.')

    def get_data(self, req):
        """
        Retrieves data from database, as requested in the req.
        :param DbRequest req: database query.
        :return: pd.DataFrame: the requested data.
        """
        symbol_db = self._get_sub_db(req.symbol)
        if symbol_db is None:
            self._logger.warning('No data for symbol "{}"'.format(req.symbol))
            return pd.DataFrame()

        conn = sqlite3.connect(symbol_db)
        data = pd.read_sql(
            sql=db_mapping[req.type],
            con=conn,
            index_col='timestamp',
            parse_dates=['timestamp'])
        return data

    def _get_sub_db(self, symbol):
        """
        Retrieves the path of a sub database.
        :param str symbol: target symbol.
        :return: str: path to the database.
        """
        sql = 'SELECT db_path FROM symbols WHERE symbol="{}"'.format(symbol)
        result = self._cursor.execute(sql).fetchone()
        if result is not None:
            return result[0]
        return self._create_sub_db(symbol)

    def _create_sub_db(self, symbol):
        """
        Creates a database for a symbol and links it in the master db.
        :param str symbol: symbol to create the db for.
        :return: str: path to the new db.
        """
        self._logger.debug('Creating database for symbol "{}"'.format(symbol))
        sub_path = os.path.join(SUB_DB_PREFIX, symbol.lower() + '.db')
        sql = 'INSERT INTO symbols (symbol, db_path) VALUES("{}","{}")'.format(symbol, sub_path)
        self._cursor.execute(sql)
        return sub_path

    def store_data(self, data):
        """
        Stores data received in a DB.
        :param StockResponse data: data to be stored.
        """
        symbol_db = self._get_sub_db(data.symbol)

        conn = sqlite3.connect(symbol_db)
        self._logger.debug('Connected to symbol database "{}"'.format(symbol_db))
        data.data.to_sql(
            name=db_mapping[data.type],
            con=conn,
            if_exists='append',
            index_label='timestamp'
        )

    def _routine(self):
        while not self._sig_interrupt:
            self._run_once()
        self._logger.debug('Module loop interrupted.')

    def _run_once(self):
        task = self._input_bus.get()
        data = self.get_data(task)
        message = StockResponse(
            timestamp=dt.datetime.now(),
            symbol=task.symbol,
            interval=task.interval,
            type=task.type,
            data=data
        )
        self._input_bus.task_done()
        self._output_bus.put(message)

    def run(self, join=False):
        if self._running:
            self._logger.warning('Module already running.')
            return

        self._connect()
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
        self._disconnect()

    def close(self):
        self.stop()
