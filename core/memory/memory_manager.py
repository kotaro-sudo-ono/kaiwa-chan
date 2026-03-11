# core/memory/memory_manager.py

from core.memory.memory_store import MemoryStore
from core.memory.models import Memory


class MemoryManager:

    def __init__(self):
        self.store = MemoryStore()

    def remember(self, content: str):

        memory = Memory.create(content)

        self.store.add(memory)

        print("memory stored:", content)

    def recall_latest(self, n=5):

        return self.store.latest(n)