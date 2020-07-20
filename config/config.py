###
# File created by Leonardo Cencetti on 7/19/20
###
import logging
from logging import Formatter, StreamHandler

# Topics
RAW_DATA_BUS = 'source_data'
DATA_REQ_BUS = 'requests'

# Master

# Logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] [%(name)s]: (%(levelname)s) %(message)s',
                    )
