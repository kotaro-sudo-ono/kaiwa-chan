# core/memory/models.py

from dataclasses import dataclass
import time


@dataclass
class Memory:

    content: str
    timestamp: float

    @staticmethod
    def create(content: str):
        return Memory(
            content=content,
            timestamp=time.time()
        )