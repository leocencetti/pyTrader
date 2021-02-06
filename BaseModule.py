#
# File created by Leonardo Cencetti on 2/5/2021
#
import logging
import threading
from dataclasses import dataclass

from enum import Enum, auto
from queue import Queue
from datetime import datetime
from time import sleep

FORMAT = '[%(levelname)s][%(name)s] %(message)s \t (%(filename)s:%(lineno)d)'


class ExecutionMode(Enum):
    PARALLEL = auto()
    SERIAL = auto()


class NodeID(Enum):
    MASTER = auto()
    ROUTER = auto()
    TEST = auto()


class NodeStatus(Enum):
    IDLING = auto()
    RUNNING = auto()
    DONE = auto()
    INTERRUPTED = auto()
    ERROR = auto()


@dataclass
class Task:
    id: int
    source: NodeID
    target: NodeID
    data: any
    datatype: type
    timestamp = datetime.now()


class Master:
    name = 'MASTER'
    id = NodeID.MASTER

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self._nodes = {}
        self._states = {}
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(logging.DEBUG)
        self.common_buffer = Queue()

    def run(self):
        for node_id in self._nodes.keys():
            self._start_node(node_id)

    def stop(self):
        for node_id in self._nodes.keys():
            self._stop_node(node_id)

    def join(self):
        for node_id in self._nodes.keys():
            self._join_node(node_id)

    def add_node(self, node_id, node, overwrite: bool = True) -> bool:
        if node_id in self._nodes:
            if not overwrite:
                self._logger.error('Could not add node {} (already present)'.format(node_id))
                return False
            else:
                self._logger.warning('Overwriting node {} (already present)'.format(node_id))
        node.common_buffer = self.common_buffer
        self._nodes[node_id] = node
        self._states[node_id] = node.state
        self._logger.info('Added node {}'.format(node_id))
        return True

    def remove_node(self, node_id) -> bool:
        if self._states[node_id] is NodeStatus.RUNNING:
            self._logger.error('Could not delete node {} (in status {})'.format(node_id, self._states[node_id]))
        self._logger.debug('Deleting node {}'.format(node_id))
        del self._nodes[node_id]
        del self._states[node_id]
        self._logger.info('Deleted node {}'.format(node_id))
        return True

    def _start_node(self, node_id) -> bool:
        if self._states[node_id] is not NodeStatus.IDLING:
            self._logger.error('Could not start node {} (in status {})'.format(node_id, self._states[node_id]))
            return False
        self._logger.debug('Starting node {}'.format(node_id))
        if self._nodes[node_id].run():
            self._logger.info('Started node {}'.format(node_id))
            return True
        else:
            self._logger.error('Could not start node {}'.format(node_id))
            return False

    def _stop_node(self, node_id) -> bool:
        if self._states[node_id] is not NodeStatus.RUNNING:
            self._logger.error('Could not stop node {} (in status {})'.format(node_id, self._states[node_id]))
            return False
        self._logger.debug('Stopping node {}'.format(node_id))
        if self._nodes[node_id].stop():
            self._logger.info('Stopped node {}'.format(node_id))
            return True
        else:
            self._logger.error('Could not stop node {}'.format(node_id))
            return False

    def _join_node(self, node_id) -> bool:
        if self._states[node_id] is not NodeStatus.RUNNING:
            self._logger.error('Could not join node {} (in status {})'.format(node_id, self._states[node_id]))
            return False
        self._logger.debug('Joining node {}'.format(node_id))
        if self._nodes[node_id].join():
            return True
        return False

    def update_status(self, node_id: NodeID, status: NodeStatus):
        self._states[node_id] = status


class BaseNode:
    def __init__(self, name: str, master: Master):
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self.state = NodeStatus.IDLING
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        self.common_buffer = None
        self.stop_requested = threading.Event()
        self._thread = None
        self.id = None
        self._master = master
        print(self._logger.level)

    def run(self) -> bool:
        if self.state is NodeStatus.RUNNING:
            self._logger.error('Already running')
            return False
        self._logger.info('Starting')
        self.state = NodeStatus.RUNNING
        self._master.update_status(self.id, self.state)
        self.stop_requested.clear()
        self._thread.start()
        return True

    def stop(self) -> bool:
        if self.state is not NodeStatus.RUNNING:
            self._logger.error('Cannot stop while in status {}'.format(self.state))
            return False
        self._logger.info('Stopping')
        self.stop_requested.set()
        if self.join():
            self._logger.info('Stopped')
            return True
        self._logger.error('Could not stop.')
        self.state = NodeStatus.INTERRUPTED
        return False

    def join(self) -> bool:
        if self.state is not NodeStatus.RUNNING:
            self._logger.error('Cannot join while in status {}'.format(self.state))
            return False
        self._logger.info('Joining')
        self._thread.join()
        self.state = NodeStatus.DONE
        return True

    def _task(self):
        self._logger.error('Did you forget to define a task?')
        self.state = NodeStatus.ERROR
        return NotImplemented


class TestNode(BaseNode):
    name = 'TEST'
    id = NodeID.TEST

    def __init__(self, master):
        super(TestNode, self).__init__(self.name, master)
        self._thread = threading.Thread(target=self._task())

    def _task(self):
        while not self.stop_requested.isSet():
            print('Hi')
            sleep(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    logging.info('Running')
    master = Master()
    testNode = TestNode(master)
    master.add_node(NodeID.TEST, testNode)
    master.run()
    sleep(10)
    master.stop()
