#
# File created by Leonardo Cencetti on 5/21/2020
#
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from plotly.colors import DEFAULT_PLOTLY_COLORS
from plotly.subplots import make_subplots

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


class DashApp:
    def __init__(self, data):
        # Initialize the app
        self.app = dash.Dash(__name__)
        self.app.config.suppress_callback_exceptions = True

        self.app.callback(
            Output("subplot", "figure"),
            [
                Input("subtypeselector", "value"),
                Input("symbolselector", "value"),
                Input("typeselector", "value"),
            ],
        )(self.update_subplots)
        self.app.callback(
            Output("subtypeselector", "options"), [Input("typeselector", "value")]
        )(self.update_subtype_dropdown)

        self.colors = DEFAULT_PLOTLY_COLORS
        self.df = data

        self.app.layout = html.Div(
            children=[
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="three columns div-user-controls",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        html.H5("Stock"),
                                        dcc.Dropdown(
                                            id="symbolselector",
                                            options=get_options(
                                                self.df["symbol"].unique()
                                            ),
                                            multi=True,
                                            value=[
                                                get_default(
                                                    self.df["symbol"].sort_values()
                                                )
                                            ],
                                            className="symbolselector",
                                            placeholder="Select a stock",
                                        ),
                                        html.H5("Data Type"),
                                        dcc.Dropdown(
                                            id="typeselector",
                                            options=get_options(
                                                self.df["type"].unique()
                                            ),
                                            value=["intraday"],
                                            className="typeselector",
                                            placeholder="Select a data type",
                                        ),
                                        html.H5("Data Subtype"),
                                        dcc.Dropdown(
                                            id="subtypeselector",
                                            options=get_options(
                                                self.df["subtype"].unique()
                                            ),
                                            value=["open"],
                                            className="subtypeselector",
                                            placeholder="Select a data subtype",
                                        ),
                                    ],
                                )
                            ],
                        ),
                        html.Div(
                            className="nine columns div-for-charts bg-grey",
                            children=[
                                dcc.Graph(
                                    id="subplot",
                                    config={"displayModeBar": True},
                                    animate=False,
                                    responsive=True,
                                    style={"height": "100%"},
                                )
                            ],
                        ),
                    ],
                )
            ]
        )

    def run(self):
        self.app.run_server(debug=True)

    def load_data(self, filename):
        self.df = pd.read_csv(filename, index_col=0, parse_dates=True)
        self.df.index = pd.to_datetime(self.df["date"])

    # Callback for second dropdown
    def update_subtype_dropdown(self, type_dropdown_value):
        s = unpack_list(type_dropdown_value)
        selected_data = self.df.loc[(self.df["type"] == s)]
        options = selected_data["subtype"].unique()
        return [{"label": i, "value": i} for i in options]

    # Callback for subplots
    def update_subplots(
        self, subtype_dropdown_value, symbol_dropdown_value, type_dropdown_value
    ):
        """Draw traces of the feature 'value' based one the currently selected stocks"""
        figure = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            subplot_titles=("title1", "title2"),
            row_heights=[0.7, 0.3],
            vertical_spacing=0.1,
        )

        # Draw and append traces for each stock
        for symbol, color in zip(symbol_dropdown_value, self.colors):
            selected_data = self.df.loc[
                (self.df["symbol"] == symbol)
                & (self.df["type"] == unpack_list(type_dropdown_value))
                & (self.df["subtype"] == unpack_list(subtype_dropdown_value))
            ]

            figure.add_trace(
                go.Scatter(
                    x=selected_data["date"],
                    y=selected_data["value"],
                    mode="lines",
                    opacity=0.7,
                    legendgroup="group",
                    line={"color": color},
                    name=symbol,
                    textposition="bottom center",
                ),
                row=1,
                col=1,
            )
            figure.add_trace(
                go.Scatter(
                    x=selected_data["date"],
                    y=selected_data["value"].diff(),
                    mode="lines",
                    opacity=0.7,
                    legendgroup="group",
                    showlegend=False,
                    line={"color": color},
                    name=symbol,
                    textposition="bottom center",
                ),
                row=2,
                col=1,
            )

        figure.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            hovermode="x",
            annotations={0: {"text": "Value"}, 1: {"text": "Change"}},
            xaxis={"gridcolor": "gray"},
            yaxis={"gridcolor": "gray", "title": {"text": "$"}},
            xaxis2={"gridcolor": "gray"},
            yaxis2={"gridcolor": "gray"},
        )
        return figure


def get_options(list_stocks):
    dict_list = []
    for i in list_stocks:
        dict_list.append({"label": i, "value": i})
    return dict_list


def get_default(list_options):
    if len(list_options) is not 1:
        return list_options[0]
    else:
        return list_options


def unpack_list(object):
    if type(object) is list:
        return object[0]
    else:
        return object
