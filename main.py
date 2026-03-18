from core.memory.memory_manager import MemoryManager
from core.memory.memory_store import MemoryStore

from core.task.task_manager import TaskManager
from core.task.task_queue import TaskQueue

from core.event.event_bus import EventBus

from core.cognition.observe import Observer

from core.cognition.think import Thinker

from integrations.voicevox import speak


def main():

    # EventBus
    event_bus = EventBus()

    # Memory
    memory_store = MemoryStore()
    memory_manager = MemoryManager(memory_store)

    # Task
    task_queue = TaskQueue()
    task_manager = TaskManager(event_bus, task_queue)

    # Observer
    observer = Observer(memory_manager, task_manager)

    context = observer.observe("hello kaiwa-chan")

    print(context)

    # thinker
    thinker = Thinker()

    thought = thinker.think(context)

    print(thought)

    # ユーザー入力
    user_input = "こんにちは、会話ちゃんです"

    # 観察
    context = observer.observe(user_input)
    print(context)

    # 音声で出力
    speak(user_input)

if __name__ == "__main__":
    main()