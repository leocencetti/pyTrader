###
# File created by Leonardo Cencetti on 2/6/21
###
import random
import string

from support.alpha_vantage_api import AVRequest, RequestType, Interval, SeriesType
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

        self.task_type = [RequestType.INTRADAY,
                          RequestType.SMA50,
                          RequestType.SMA200,
                          RequestType.EMA50,
                          RequestType.EMA200]

    def _job(self):
        while not self._stop_requested.isSet():
            for s in self.symbols:
                for d in self.task_type:
                    self._send(NodeID.WATCHER, AVRequest(
                        key=key_generator(),
                        type=d,
                        interval=Interval.MIN1,
                        symbol=s,
                        series=SeriesType.CLOSE))
            self._stop_requested.wait(60)
