#
# File created by Leonardo Cencetti on 5/10/2020
#
import random
import string
from queue import Queue

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

from task_master import TaskMaster


def key_generator(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def fetchStocks(symbols, data_types, num_workers=10):
    taskQueue = Queue()
    for s in symbols:
        for d in data_types:
            taskQueue.put({
                'task_type': d,
                'key'      : key_generator(),
                'symbol'   : s})

    taskMaster = TaskMaster(taskQueue, num_workers)
    taskMaster.start()
    taskQueue.join()
    taskMaster.stop()
    return taskMaster.getData()


def multiPlot(data, attribute, addAll=True):
    """
    :param str attribute: sub column name
    :param dict data: dataframe with stocks as columns and rows as date of the stock price
    :param bool addAll: dropdown button to display all stocks at once
    :return:
    """
    layout = dict(title=attribute, title_x=0.5)
    fig = go.Figure(layout=layout)

    for column in data.keys():
        fig.add_trace(
            go.Scatter(
                x=data[column].index,
                y=data[column][attribute],
                name=column
            )
        )

    button_all = dict(label='All',
                      method='restyle',
                      args=[{'visible'   : [True for _ in data.keys()],
                             'title'     : 'All',
                             'showlegend': True}])

    def create_layout_button(col):
        return dict(label=col,
                    method='restyle',
                    args=[{'visible'   : [k == col for k in data.keys()],
                           'title'     : col,
                           'showlegend': True}])

    fig.update_layout(
        updatemenus=[
            dict(active=0,
                 buttons=([button_all] * addAll) + [create_layout_button(col) for col in data.keys()])])

    # fig.show()

    app = dash.Dash()
    app.layout = html.Div([
        dcc.Graph(
            style={'height': '90vh'},
            figure=fig)
    ])
    app.run_server(host='0.0.0.0', port=8050, debug=True, use_reloader=False)
