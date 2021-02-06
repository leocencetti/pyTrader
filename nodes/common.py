###
# File created by Leonardo Cencetti on 2/6/21
###
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from queue import Queue

class CustomEnum(Enum):
    def __str__(self):
        return '%s' % self._name_


class ExecutionMode(CustomEnum):
    PARALLEL = auto()
    SERIAL = auto()


class NodeID(CustomEnum):
    MASTER = auto()
    ROUTER = auto()
    TESTF = auto()
    TESTC = auto()
    WATCHER = auto()
    BROKER = auto()
    PROCESSOR = auto()


class NodeState(CustomEnum):
    IDLING = auto()  # Node never started
    RUNNING = auto()  # Node running
    STOPPING = auto()  # Node asked to stop
    DONE = auto()  # Node has finished
    STOPPED = auto()  # Node has been interrupted (after STOPPING)
    ERROR = auto()  # Node has errors


@dataclass
class Task:
    timestamp = datetime.now()
    source: NodeID
    target: NodeID
    data: any


class Buffer:
    def __init__(self):
        self._queues = {}
        for node_id in NodeID:
            self._queues[node_id] = Queue()

    def __getitem__(self, node_id: NodeID):
        return self._queues[node_id]

    def flush(self, node_id: NodeID):
        with self._queues[node_id].mutex:
            self._queues[node_id].queue.clear()
