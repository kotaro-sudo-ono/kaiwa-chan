# core/memory/memory_store.py
import json
from pathlib import Path

MEMORY_FILE = Path("memory.json")


class MemoryStore:

    def __init__(self):
        self.memories = []
        self._load()

    def _load(self):
        if MEMORY_FILE.exists():
            self.memories = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))

    def _save(self):
        MEMORY_FILE.write_text(json.dumps(self.memories, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, memory):
        self.memories.append(memory)
        self._save()

    def list_all(self):
        return self.memories

    def latest(self, n=5):
        return self.memories[-n:]

    def get_all(self):
        return self.memories