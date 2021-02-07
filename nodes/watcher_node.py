###
# File created by Leonardo Cencetti on 2/6/21
###
from nodes import BaseNode, NodeID, ExecutionMode
from support.alpha_vantage_api import get_intraday, get_sma, get_ema, RequestType, AVRequest


class WatcherNode(BaseNode):
    id = NodeID.WATCHER

    def __init__(self, master_node):
        super(WatcherNode, self).__init__(self.id, master_node, ExecutionMode.PARALLEL)

    def _process_task(self, task):
        r: AVRequest = task.data
        interval = r.interval.value
        series = r.series.value
        if r.type is RequestType.SMA50:
            data = get_sma(r.symbol, r.key, interval, time_period=50, series_type=series)
        elif r.type is RequestType.SMA200:
            data = get_sma(r.symbol, r.key, interval, time_period=200, series_type=series)
        elif r.type is RequestType.EMA50:
            data = get_ema(r.symbol, r.key, interval, time_period=50, series_type=series)
        elif r.type is RequestType.EMA200:
            data = get_ema(r.symbol, r.key, interval, time_period=200, series_type=series)
        elif r.type is RequestType.INTRADAY:
            data = get_intraday(r.symbol, r.key, interval)
        elif r.type is RequestType.FULL_INTRADAY:
            data = get_intraday(r.symbol, r.key, interval, outputsize='full')
        else:
            self._logger.warning('Unknown task type {}'.format(r.type))
            return
        self._send(NodeID.PROCESSOR, data)
