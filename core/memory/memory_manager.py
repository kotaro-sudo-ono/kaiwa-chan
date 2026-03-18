from core.memory.memory_store import MemoryStore
from core.memory.models import Memory


class MemoryManager:

    def __init__(self, store: MemoryStore):
        self.store = store
    
    def add_memory(self, text: str):
        # 記憶ストアに追加
        self.store.add(text)

    def remember(self, content: str):

        memory = Memory.create(content)

        self.store.add(memory)

        print("memory stored:", content)

    def recall_latest(self, n=5):

        return self.store.latest(n)

    def get_all(self):
        return self.store.get_all()