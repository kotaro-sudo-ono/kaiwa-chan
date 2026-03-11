from .task_model import Task
from .task_queue import TaskQueue


class TaskManager:

    def __init__(self):
        self.queue = TaskQueue()

    def create_task(self, task_type: str, payload):
        task = Task.create(task_type, payload)
        self.queue.push(task)
        return task

    def get_next_task(self):
        if self.queue.is_empty():
            return None
        return self.queue.pop()