###
# File created by Leonardo Cencetti on 2/6/21
###
from .base_node import BaseNode
from .broker_node import BrokerNode
from .common import Mode, NodeID, NodeState, Task
from .dashboard_node import DashboardNode
from .master_node import MasterNode
from .processor_node import ProcessorNode
from .router_node import RouterNode
from .test_node import TestNodeConsumer, TestNodeFeeder
from .watcher_node import WatcherNode

NodeFactory = {
    NodeID.MASTER: MasterNode,
    NodeID.BROKER: BrokerNode,
    NodeID.WATCHER: WatcherNode,
    NodeID.PROCESSOR: ProcessorNode,
    NodeID.TESTF: TestNodeFeeder,
    NodeID.TESTC: TestNodeConsumer,
    NodeID.ROUTER: RouterNode,
    NodeID.DASHBOARD: DashboardNode,
}
