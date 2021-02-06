###
# File created by Leonardo Cencetti on 2/6/21
###
from nodes import BaseNode, NodeID
from support.alpha_vantage_api import get_intraday, get_sma, get_ema


class WatcherNode(BaseNode):
    id = NodeID.WATCHER

    def __init__(self, master_node):
        super(WatcherNode, self).__init__(self.id, master_node)

    def _process_task(self, task):
        key = task.data['key']
        symbol = task.data['symbol']
        series_type = 'close'
        if task.data['task_type'] == 'sma50':
            data = get_sma(symbol=symbol, key=key, interval='1min', time_period=50, series_type=series_type)
        elif task.data['task_type'] == 'sma200':
            data = get_sma(symbol=symbol, key=key, interval='1min', time_period=200, series_type=series_type)
        elif task.data['task_type'] == 'ema50':
            data = get_ema(symbol=symbol, key=key, interval='1min', time_period=50, series_type=series_type)
        elif task.data['task_type'] == 'ema200':
            data = get_ema(symbol=symbol, key=key, interval='1min', time_period=200, series_type=series_type)
        elif task.data['task_type'] == 'intraday':
            data = get_intraday(symbol, key)
        elif task.data['task_type'] == 'fintraday':
            data = get_intraday(symbol, key, outputsize='full')
        else:
            self._logger.warning('Unknown task type {}'.format(task.data['task_type']))
            return
        self._send(NodeID.PROCESSOR, data)
