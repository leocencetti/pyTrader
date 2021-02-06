###
# File created by Leonardo Cencetti on 2/6/21
###
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto


class ExecutionMode(Enum):
    PARALLEL = auto()
    SERIAL = auto()


class NodeID(Enum):
    MASTER = auto()
    ROUTER = auto()
    TEST = auto()


class NodeState(Enum):
    IDLING = auto()  # Node never started
    RUNNING = auto()  # Node running
    STOPPING = auto()  # Node asked to stop
    DONE = auto()  # Node has finished
    STOPPED = auto()  # Node has been interrupted (after STOPPING)
    ERROR = auto()  # Node has errors


@dataclass
class Task:
    id: int
    source: NodeID
    target: NodeID
    data: any
    datatype: type
    timestamp = datetime.now()
