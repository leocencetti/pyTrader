###
# File created by Leonardo Cencetti on 2/6/21
###
import random
import string
from time import sleep

from .base_node import BaseNode
from .common import NodeID


def key_generator(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class BrokerNode(BaseNode):
    id = NodeID.BROKER

    def __init__(self, master_node):
        super(BrokerNode, self).__init__(self.id, master_node)
        with open('data/stock_symbols.txt') as f:
            self.symbols = f.read().splitlines()

        self.task_type = ['fintraday', 'sma50', 'sma200', 'ema50', 'ema200']

    def _job(self):
        while not self._stop_requested.isSet():
            for s in self.symbols:
                for d in self.task_type:
                    self._send(NodeID.WATCHER, {
                        'task_type': d,
                        'key'      : key_generator(),
                        'symbol'   : s})
            sleep(1)
