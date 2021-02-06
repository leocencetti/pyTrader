###
# File created by Leonardo Cencetti on 2/6/21
###
from time import sleep

from nodes import NodeID, MasterNode, TestNode

if __name__ == '__main__':
    master = MasterNode()
    testNode = TestNode(master)
    master.add_node(NodeID.TEST, testNode)
    master.run()
    sleep(10)
    master.stop()
