#
# File created by Leonardo Cencetti on 2/5/2021
#
from threading import Event, Thread
from .common import NodeState
from utils.custom_logger import *


class BaseNode:
    def __init__(self, name: str, master_node):
        self._state = NodeState.IDLING
        self._logger = logging.getLogger(name=name)
        self.common_buffer = None
        self._stop_requested = Event()
        self._thread = Thread()
        self._master = master_node
        self._logger.info('Initialized')

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._master.update_status(self.id, value)
        self._state = value

    def run(self) -> bool:
        if self.state is NodeState.RUNNING:
            self._logger.error('Already running')
            return False
        self._logger.info('Starting thread')
        self._stop_requested.clear()
        self.state = NodeState.RUNNING
        self._thread.start()
        return True

    def stop(self) -> bool:
        if self.state is not NodeState.RUNNING:
            self._logger.error('Cannot stop while in status {}'.format(self.state))
            return False
        self._logger.info('Stop requested')
        self._stop_requested.set()
        self.state = NodeState.STOPPING
        return True

    def join(self) -> bool:
        if self.state not in [NodeState.RUNNING, NodeState.STOPPING]:
            self._logger.error('Cannot join while in status {}'.format(self.state))
            return False
        self._logger.info('Joining thread')
        self._thread.join()
        self.state = NodeState.STOPPED if self._stop_requested.isSet() else NodeState.DONE
        return True

    def _task(self):
        self._logger.error('Did you forget to define a task?')
        self.state = NodeState.ERROR
        return NotImplemented
