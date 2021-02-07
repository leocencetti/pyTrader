#
# File created by Leonardo Cencetti on 2/5/2021
#
from queue import Empty
from threading import Event, Thread

from utils.custom_logger import *
from .common import NodeState, Task, NodeID, ExecutionMode
from .master_node import MasterNode


class BaseNode:
    MAX_THREADS = 4

    def __new__(cls, *args, **kwargs):
        # prevent instantiation
        if cls is BaseNode:
            raise TypeError('{} cannot be instantiated'.format(cls))
        return object.__new__(cls)

    def __init__(self, node_id: NodeID, master_node: MasterNode, mode: ExecutionMode = ExecutionMode.SERIAL):
        self.mode = mode
        self._state = NodeState.IDLING
        self._logger = logging.getLogger(name=str(node_id))
        self.common_buffer = None
        self._stop_requested = Event()
        self._job_done = Event()
        if self.mode is ExecutionMode.SERIAL:
            self._thread = Thread(target=self._main_loop, daemon=True)
        else:
            self._threads = [Thread(target=self._main_loop, daemon=True) for _ in range(self.MAX_THREADS)]
        self._master = master_node
        self._logger.debug('Initialized')

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._master.update_status(self.id, value)
        self._state = value

    def run(self) -> bool:
        if self.state is NodeState.RUNNING:
            self._logger.warning('Already running')
            return False
        self._logger.debug('Starting thread')
        self._stop_requested.clear()
        self._job_done.clear()
        self.state = NodeState.RUNNING
        if self.mode is ExecutionMode.SERIAL:
            self._thread.start()
            return True
        for T in self._threads:
            T.start()

    def stop(self) -> bool:
        if self.state is not NodeState.RUNNING:
            self._logger.warning('Cannot stop while in status {}'.format(self.state.name))
            return False
        self._logger.debug('Stopping thread')
        self._stop_requested.set()
        self.state = NodeState.STOPPING
        return True

    def join(self) -> bool:
        if self.state not in [NodeState.RUNNING, NodeState.STOPPING]:
            self._logger.warning('Cannot join while in status {}'.format(self.state.name))
            return False
        self._logger.debug('Joining thread')
        if self.mode is ExecutionMode.SERIAL:
            self._thread.join()
        else:
            for T in self._threads:
                T.join()
        self.state = NodeState.STOPPED if self._stop_requested.isSet() else NodeState.DONE
        return True

    def _job(self):
        try:
            task = self.common_buffer[self.id].get(timeout=30)
        except Empty:
            self._logger.info('No task received in the last 30s. Stopping.')
            self._job_done.set()
            return

        if not self._is_valid(task):
            self.common_buffer[self.id].task_done()
            return
        self._process_task(task)
        self.common_buffer[self.id].task_done()

    def _main_loop(self):
        while not self._stop_requested.isSet():
            self._job()
            if self._job_done.isSet():
                self.state = NodeState.DONE
                return
        self.state = NodeState.STOPPED

    def _is_valid(self, task: Task) -> bool:
        if task.target is not self.id:
            self._logger.warning('Received task for node {}, ignoring'.format(task.target.name))
            return False
        return True

    def _send(self, target: NodeID, data: any):
        self.common_buffer[target].put(Task(self.id, target, data))

    def _process_task(self, task: Task):
        self._logger.error('Did you forget to define a task processor?')
        self.state = NodeState.ERROR
        return NotImplemented
