###
# File created by Leonardo Cencetti on 3/31/20
###
from itertools import cycle
from queue import Queue
from master import TaskMaster
from time import sleep

with open('alpha_vantage_api.key', 'r') as f:
    keys = cycle(f.read().splitlines())
with open('stock_symbols.txt') as f:
    # symbols = cycle(f.read().splitlines())
    symbols = f.read().splitlines()
taskQueue = Queue()
for s in symbols:
    taskQueue.put({'key': next(keys), 'symbol': s})

taskMaster = TaskMaster(taskQueue, interval=0.02)
taskMaster.start()
sleep(120)
taskMaster.stop()
