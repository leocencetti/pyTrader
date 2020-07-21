###
# File created by Leonardo Cencetti on 7/19/20
###
import logging

# Topics
RAW_DATA_BUS = 'source_data'
RAW_REQ_BUS = 'raw_requests'
DB_RES_BUS = 'db_data'
DB_REQ_BUS = 'db_request'

# Master

# Logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] [%(name)s]: (%(levelname)s) %(message)s',
                    )

# Storage
DB_PATH = 'db/master.db'
SUB_DB_PREFIX = 'db/symbols'
db_mapping = dict(
    intraday='intraday',
    full_intraday='intraday',
    sma50='sma50',
    sma200='sma200',
    ema50='ema50',
    ema200='ema200'
)
