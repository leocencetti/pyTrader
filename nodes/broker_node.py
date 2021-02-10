###
# File created by Leonardo Cencetti on 2/8/21
###
###
# File created by Leonardo Cencetti on 2/6/21
###

from .base_node import BaseNode
from .common import NodeID, Mode


class BrokerNode(BaseNode):
    id = NodeID.BROKER

    def __init__(self, master_node):
        super(BrokerNode, self).__init__(self.id, master_node)
        # self._degiro = degiroapi.DeGiro()
        # self._degiro.login(auth2fa=True)
        #
        # cashfunds = self._degiro.getdata(degiroapi.Data.Type.CASHFUNDS)
        # for data in cashfunds:
        #     print(data)
        #
        # portfolio = self._degiro.getdata(degiroapi.Data.Type.PORTFOLIO)
        # for data in portfolio:
        #     print(data)
        #
        # transactions = self._degiro.transactions(datetime(2019, 1, 1), datetime.now())
        # print(pretty_json(transactions))
        #
        # self._degiro.logout()

    def _process_task(self, task):
        pass
        # r: AVRequest = task.data
        # interval = r.interval.value
        # series = r.series.value
        # if r.type is RequestType.SMA50:
        #     data = get_sma(r.symbol, r.key, interval, time_period=50, series_type=series)
        # elif r.type is RequestType.SMA200:
        #     data = get_sma(r.symbol, r.key, interval, time_period=200, series_type=series)
        # elif r.type is RequestType.EMA50:
        #     data = get_ema(r.symbol, r.key, interval, time_period=50, series_type=series)
        # elif r.type is RequestType.EMA200:
        #     data = get_ema(r.symbol, r.key, interval, time_period=200, series_type=series)
        # elif r.type is RequestType.INTRADAY:
        #     data = get_intraday(r.symbol, r.key, interval)
        # elif r.type is RequestType.FULL_INTRADAY:
        #     data = get_intraday(r.symbol, r.key, interval, outputsize='full')
        # else:
        #     self._logger.warning('Unknown task type {}'.format(r.type))
        #     return
        # self._send(NodeID.PROCESSOR, data)
