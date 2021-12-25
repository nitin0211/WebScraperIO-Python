
from queue import Queue


class TaskQueue(object):

    def __init__(self):
        self.queue = Queue()

    def add(self, job):
        # TODO Maintain a global cache and use the SimHash or BloomFilter algorithm implemented by redis to filter

        if not self.is_full():
            self.queue.put(job, block=False)
            return True
        else:
            return False

    def get_task_queue_size(self):
        return self.queue.qsize()

    def is_full(self):
        return True if self.queue.full() else False

    def get_next_job(self):
        if not self.queue.empty():
            return self.queue.get(block=False)
        else:
            return False
