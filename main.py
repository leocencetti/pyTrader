###
# File created by Leonardo Cencetti on 3/31/20
###
import pandas as pd

from dash_app import DashApp
from wrappers import fetchStocks

mode = 'run'

if mode == 'get':
    with open('stock_symbols.txt') as f:
        symbols_list = f.read().splitlines()

    task_list = ['fintraday', 'sma50', 'sma200', 'ema50', 'ema200']
    data = fetchStocks(symbols_list, task_list)
    data.to_pickle('data/backup.pkl')
elif mode == 'run':
    data = pd.read_pickle('data/backup.pkl')
    dash_app = DashApp(data)
    dash_app.run()
