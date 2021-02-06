###
# File created by Leonardo Cencetti on 2/6/21
###
import pandas as pd

from .base_node import BaseNode
from .common import NodeID

pd.options.plotting.backend = 'plotly'


class ProcessorNode(BaseNode):
    id = NodeID.PROCESSOR

    def __init__(self, master_node):
        super(ProcessorNode, self).__init__(self.id, master_node)

    def _process_task(self, task):
        fig = task.data.plot(y='value')
        fig.show()
