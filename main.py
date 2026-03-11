from core.task.task_manager import TaskManager


def main():

    task_manager = TaskManager()

    task_manager.create_task(
        "print_message",
        {"message": "hello kaiwa-chan"}
    )

    task = task_manager.get_next_task()

    print(task)


if __name__ == "__main__":
    main()