# core/memory/memory_store.py

class MemoryStore:

    def __init__(self):
        self.memories = []

    def add(self, memory):
        self.memories.append(memory)

    def list_all(self):
        return self.memories

    def latest(self, n=5):
        return self.memories[-n:]

    
    def get_all(self):
        return self.memories