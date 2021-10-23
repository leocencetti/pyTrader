###
# File created by Leonardo Cencetti on 2/6/21
###
from time import sleep

from nodes import MasterNode, NodeID

if __name__ == '__main__':
    master = MasterNode()
    master.add_node(NodeID.WATCHER)
    master.add_node(NodeID.PROCESSOR)
    master.add_node(NodeID.BROKER)
    master.add_node(NodeID.ROUTER)
    master.add_node(NodeID.DASHBOARD)
    master.run()
    sleep(10)
    master._nodes[NodeID.WATCHER].stop()
    master.join()
