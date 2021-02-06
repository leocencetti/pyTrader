###
# File created by Leonardo Cencetti on 2/6/21
###
import signal
import sys
from queue import Queue
from threading import Event

from .common import NodeID, NodeState
from utils.custom_logger import *


class MasterNode:
    name = 'MASTER'
    id = NodeID.MASTER

    def interrupt_handler(self, signal, frame):
        sys.stderr.write("\r")
        if self._stop_requested.isSet():
            self._logger.warning('Second Ctrl+C Registered. Killing.')
            sys.exit(0)
        self._logger.info('Ctrl+C Registered. Exiting.')
        self.stop()

    def __init__(self):
        self.state = NodeState.IDLING
        self._nodes = {}
        self._node_states = {}
        self._logger = logging.getLogger(name=self.name)
        self.common_buffer = Queue()
        self._stop_requested = Event()
        signal.signal(signal.SIGINT, self.interrupt_handler)

    def run(self):
        """ Run all nodes """
        if self.state is NodeState.RUNNING:
            self._logger.error('Already running')
            return
        self._stop_requested.clear()
        for node_id in self._nodes.keys():
            self._start_node(node_id)
        self.state = NodeState.RUNNING

    def stop(self):
        """ Stop all nodes """
        if self._stop_requested.isSet():
            self._logger.debug('Stop already requested.')
            return
        if self.state is not NodeState.RUNNING:
            self._logger.error('Cannot stop while in status {}'.format(self.state))
            return
        self._stop_requested.set()
        for node_id in self._nodes.keys():
            self._stop_node(node_id)
        self.state = NodeState.STOPPING

    def join(self):
        """ Join nodes sequentially """
        if self.state not in [NodeState.RUNNING, NodeState.STOPPING]:
            self._logger.error('Cannot join while in status {}'.format(self.state))
            return
        for node_id in self._nodes.keys():
            self._join_node(node_id)
        self.state = NodeState.STOPPED

    def add_node(self, node_id, node, overwrite: bool = True) -> bool:
        """

        :param node_id:
        :param node:
        :param overwrite:
        :return:
        """
        if node_id in self._nodes:
            if not overwrite:
                self._logger.error('Could not add node {} (already present)'.format(node_id))
                return False
            else:
                self._logger.warning('Overwriting node {} (already present)'.format(node_id))
        node.common_buffer = self.common_buffer
        self._nodes[node_id] = node
        self._node_states[node_id] = node.state
        self._logger.info('Added node {}'.format(node_id))
        return True

    def remove_node(self, node_id) -> bool:
        """

        :param node_id:
        :return:
        """
        if self._node_states[node_id] is NodeState.RUNNING:
            self._logger.error('Could not delete node {} (in status {})'.format(node_id, self._node_states[node_id]))
        self._logger.debug('Deleting node {}'.format(node_id))
        del self._nodes[node_id]
        del self._node_states[node_id]
        self._logger.info('Deleted node {}'.format(node_id))
        return True

    def _start_node(self, node_id) -> bool:
        if self._node_states[node_id] is not NodeState.IDLING:
            self._logger.error('Could not start node {} (in status {})'.format(node_id, self._node_states[node_id]))
            return False
        self._logger.debug('Starting node {}'.format(node_id))
        if self._nodes[node_id].run():
            self._logger.info('Started node {}'.format(node_id))
            return True
        else:
            self._logger.error('Could not start node {}'.format(node_id))
            return False

    def _stop_node(self, node_id) -> bool:
        print('here')
        if self._node_states[node_id] is not NodeState.RUNNING:
            self._logger.error('Could not stop node {} (in status {})'.format(node_id, self._node_states[node_id]))
            return False
        self._logger.debug('Stopping node {}'.format(node_id))
        if self._nodes[node_id].stop():
            self._logger.info('Stopped node {}'.format(node_id))
            return True
        else:
            self._logger.error('Could not stop node {}'.format(node_id))
            return False

    def _join_node(self, node_id) -> bool:
        if self._node_states[node_id] not in [NodeState.RUNNING, NodeState.STOPPING]:
            self._logger.error('Could not join node {} (in status {})'.format(node_id, self._node_states[node_id]))
            return False
        self._logger.debug('Joining node {}'.format(node_id))
        if self._nodes[node_id].join():
            return True
        return False

    def update_status(self, node_id: NodeID, status: NodeState):
        """

        :param node_id:
        :param status:
        """
        self._node_states[node_id] = status

