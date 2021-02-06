###
# File created by Leonardo Cencetti on 2/6/21
###
from threading import Thread
from time import sleep

from .base_node import BaseNode
from .common import NodeID


class TestNode(BaseNode):
    name = 'TEST'
    id = NodeID.TEST

    def __init__(self, master_node):
        super(TestNode, self).__init__(self.name, master_node)
        self._thread = Thread(target=self._task, daemon=True)

    def _task(self):
        while not self._stop_requested.isSet():
            self._logger.info('Hi')
            sleep(1)
