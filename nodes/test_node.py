###
# File created by Leonardo Cencetti on 2/6/21
###
from time import sleep

from .base_node import BaseNode
from .common import NodeID, Task


class TestNodeFeeder(BaseNode):
    name = "TESTF"
    id = NodeID.TESTF

    def __init__(self, master_node):
        super(TestNodeFeeder, self).__init__(self.name, master_node)

    def _job(self):
        target = NodeID.TESTC
        while not self._stop_requested.isSet():
            self.common_buffer[target].put(Task(self.id, target, "Hi"))
            sleep(1)


class TestNodeConsumer(BaseNode):
    id = NodeID.TESTC

    def __init__(self, master_node):
        super(TestNodeConsumer, self).__init__(self.id, master_node)

    def _process_task(self, task):
        self._logger.info(task.data)
        sleep(1)
