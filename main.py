###
# File created by Leonardo Cencetti on 3/31/20
###
import pandas as pd

from scripts.dash_app import DashApp
from support.wrappers import fetch_data

mode = 'run'

if mode == 'get':
    with open('data/stock_symbols.txt') as f:
        symbols_list = f.read().splitlines()

    task_list = ['full_intraday', 'sma50', 'sma200', 'ema50', 'ema200']
    data = fetch_data(symbols_list, task_list)
    data.to_pickle('data/backup.pkl')
elif mode == 'run':
    data = pd.read_pickle('data/backup.pkl')
    dash_app = DashApp(data)
    dash_app.run()
