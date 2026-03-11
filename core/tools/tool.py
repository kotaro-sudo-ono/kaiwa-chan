# core/tools/tool.py

from typing import Callable


class Tool:

    def __init__(self, name: str, func: Callable):
        self.name = name
        self.func = func

    def execute(self, *args, **kwargs):
        return self.func(*args, **kwargs)