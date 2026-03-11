from queue import Queue
from .task_model import Task


class TaskQueue:

    def __init__(self):
        self.queue = Queue()

    def push(self, task: Task):
        self.queue.put(task)

    def pop(self) -> Task:
        return self.queue.get()

    def is_empty(self):
        return self.queue.empty()