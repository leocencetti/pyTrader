###
# File created by Leonardo Cencetti on 3/31/20
###
from itertools import cycle
from queue import Queue
from task_master import TaskMaster
from time import sleep, time
import string
import random


def key_generator(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


t0 = time()
with open('stock_symbols.txt') as f:
    # symbols = cycle(f.read().splitlines())
    symbols = f.read().splitlines()
taskQueue = Queue()
for s in symbols:
    taskQueue.put({
        'task_type': '',
        'key': key_generator(),
        'symbol': s})

taskMaster = TaskMaster(taskQueue, num_workers=10)
taskMaster.start()
taskQueue.join()
taskMaster.stop()
t1 = time()
print('Total time: ', t1 - t0)
