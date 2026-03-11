from collections import defaultdict
from typing import Callable


class EventBus:

    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable):
        self.listeners[event_type].append(handler)

    def emit(self, event_type: str, data=None):
        handlers = self.listeners[event_type]

        for handler in handlers:
            handler(data)