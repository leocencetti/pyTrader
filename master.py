###
# File created by Leonardo Cencetti on 3/31/20
###
from worker import Worker
from time import sleep


class TaskMaster:
    def __init__(self, queue, num_workers=5, interval=12):
        self.queue = queue
        self._threads = []
        self._num_workers = num_workers
        self.data = None
        self._interval = interval

        for i in range(self._num_workers):
            t = Worker(self.queue, self.data, self._interval)
            self._threads.append(t)

    def start(self, blocking=False):
        print('[TaskMaster] Starting workers...')
        for t in self._threads:
            t.run()
            sleep(self._interval)
        print('[TaskMaster] Started all workers.')
        if blocking:
            print('[TaskMaster] Waiting for workers to finish.')
            for t in self._threads:
                t.join()

    def stop(self):
        print('[TaskMaster] Stopping workers...')
        with self.queue.mutex:
            self.queue.queue.clear()
        for i in range(self._num_workers):
            self.queue.put(None)
        for t in self._threads:
            t.join()
        print('[TaskMaster] Stopped all workers.')
