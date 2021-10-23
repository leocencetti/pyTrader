###
# File created by Leonardo Cencetti on 2/6/21
###

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from support.alpha_vantage_api import AVReply, RequestType
from .base_node import BaseNode
from .common import NodeID

pd.options.plotting.backend = "plotly"


class ProcessorNode(BaseNode):
    id = NodeID.PROCESSOR

    def __init__(self, master_node):
        super(ProcessorNode, self).__init__(self.id, master_node)

    def _process_task(self, task):
        self._plot(task.data)

    def _plot(self, reply: AVReply):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        if reply.type in [RequestType.INTRADAY, RequestType.FULL_INTRADAY]:
            fig.add_trace(
                go.Candlestick(
                    x=reply.data.index,
                    open=reply.data["open"],
                    high=reply.data["high"],
                    close=reply.data["close"],
                    low=reply.data["low"],
                    name="{} OHLC".format(reply.symbol),
                ),
                secondary_y=False,
            )
            if "volume" in reply.data.columns:
                fig.add_trace(
                    go.Bar(
                        x=reply.data.index,
                        y=reply.data["volume"],
                        name="{} Volume".format(reply.symbol),
                        opacity=0.2,
                        marker_color="blue",
                    ),
                    secondary_y=True,
                )

        if reply.type in [
            RequestType.EMA50,
            RequestType.EMA200,
            RequestType.SMA50,
            RequestType.SMA200,
        ]:
            fig.add_trace(
                go.Scatter(x=reply.data.index, y=reply.data[reply.type.value])
            )

        fig.update_layout(
            title="{} for symbol {}".format(reply.type, reply.symbol),
            yaxis_title="USD per Share",
            yaxis_fixedrange=False,
        )
        fig.update_xaxes(
            rangeslider_yaxis_rangemode="auto",
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=15, label="15m", step="minute", stepmode="backward"),
                        dict(count=30, label="30m", step="minute", stepmode="backward"),
                        dict(count=45, label="45m", step="minute", stepmode="backward"),
                        dict(count=1, label="HTD", step="hour", stepmode="todate"),
                        dict(count=3, label="3h", step="hour", stepmode="backward"),
                        dict(count=1, label="1d", step="day", stepmode="backward"),
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=14, label="2w", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=3, label="3m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(step="all"),
                    ]
                )
            ),
        )
        fig.show()
