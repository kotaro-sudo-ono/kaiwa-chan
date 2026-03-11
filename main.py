from core.event.event_bus import EventBus
from core.task.task_manager import TaskManager

from core.tools.registry import ToolRegistry
from core.tools.tool import Tool

from agents.base_agent import BaseAgent
from runtime.scheduler import Scheduler
from core.memory.memory_manager import MemoryManager


def print_message(message):
    print("tool executed:", message)


def main():

    event_bus = EventBus()

    task_manager = TaskManager(event_bus)

    tool_registry = ToolRegistry()

    memory_manager = MemoryManager()

    tool_registry.register(
        Tool("print_message", print_message)
    )

    agent = BaseAgent(
        task_manager,
        tool_registry,
        memory_manager
    )

    scheduler = Scheduler(agent)

    task_manager.create_task(
        "print_message",
        {"message": "hello kaiwa-chan"}
    )

    scheduler.start(max_steps=3)


if __name__ == "__main__":
    main()