class Observer:

    def __init__(self, memory_manager, task_manager):
        self.memory_manager = memory_manager
        self.task_manager = task_manager

    def observe(self, user_input: str):

        context = {
            "user_input": user_input,
            "memory": self.memory_manager.get_all(),
            "tasks": self.task_manager.get_all_tasks(),
        }

        return context