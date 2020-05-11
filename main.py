###
# File created by Leonardo Cencetti on 3/31/20
###
from wrappers import fetchStocks, multiPlot


with open('stock_symbols.txt') as f:
    symbols_list = f.read().splitlines()

data = fetchStocks(symbols_list)
multiPlot(data, '1. open')
