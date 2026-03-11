from core.event.event_bus import EventBus
from core.event.event_types import TASK_CREATED
from core.task.task_manager import TaskManager


def on_task_created(task):
    print("task created:", task)


def main():

    event_bus = EventBus()

    event_bus.subscribe(
        TASK_CREATED,
        on_task_created
    )

    task_manager = TaskManager(event_bus)

    task_manager.create_task(
        "print_message",
        {"message": "hello kaiwa-chan"}
    )

if __name__ == "__main__":
    main()