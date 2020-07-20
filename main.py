###
# File created by Leonardo Cencetti on 3/31/20
###
import logging
import signal
import sys

from modules.master import Master

logger = logging.getLogger(__name__)
master = Master()


def exit_gracefully(sig, frame):
    logger.info('Received {}: exiting...'.format(sig))
    master.close()
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    master.run()
    master.stop()