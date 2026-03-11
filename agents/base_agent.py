# agents/base_agent.py

class BaseAgent:

    def __init__(self, task_manager, tool_registry, memory_manager):

        self.task_manager = task_manager
        self.tool_registry = tool_registry
        self.memory_manager = memory_manager

    def run_once(self):

        task = self.task_manager.get_next_task()

        if not task:
            print("no task")
            return

        tool = self.tool_registry.get(task.type)

        if not tool:
            print("tool not found:", task.type)
            return

        tool.execute(**task.payload)

        task.status = "completed"

        self.memory_manager.remember(
            f"task {task.type} executed"
        )

        print("task completed:", task.id)