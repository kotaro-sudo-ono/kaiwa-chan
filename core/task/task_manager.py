from core.event.event_bus import EventBus
from core.event.event_types import TASK_CREATED
from .task_model import Task
from .task_queue import TaskQueue

class TaskManager:

    def __init__(self, event_bus, task_queue):
        self.queue = TaskQueue()
        self.event_bus = event_bus
        self.task_queue = task_queue


    def create_task(self, task_type: str, payload):
        task = Task.create(task_type, payload)

        self.queue.push(task)

        self.event_bus.emit(
            TASK_CREATED,
            task
        )

        return task

    def get_next_task(self):
        if self.queue.is_empty():
            return None
        return self.queue.pop()
    
    def get_all_tasks(self):
        return self.task_queue.get_all()